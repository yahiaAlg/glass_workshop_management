from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from datetime import datetime, timedelta
from apps.invoices.models import Invoice
from apps.customers.models import Customer
from apps.orders.models import Order
from apps.inventory.models import GlassProduct

from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Avg, F, Max, Min
from django.db.models.functions import TruncMonth

import csv
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import xlsxwriter

from apps.invoices.models import Invoice, InvoiceItem
from apps.customers.models import Customer
from apps.inventory.models import GlassProduct
from apps.orders.models import Order
from apps.company.models import Company

@login_required
def dashboard_home(request):
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Key metrics
    today_sales = Invoice.objects.filter(
        invoice_date=today, 
        status__in=['sent', 'paid']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    month_revenue = Invoice.objects.filter(
        invoice_date__gte=this_month,
        status__in=['sent', 'paid']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    total_customers = Customer.objects.filter(status='active').count()
    
    # Low stock products
    low_stock_products = [p for p in GlassProduct.objects.filter(status='active') if p.is_low_stock()]
    low_stock_count = len(low_stock_products)
    
    pending_orders = Order.objects.filter(status='pending').count()
    outstanding_invoices = Invoice.objects.filter(status__in=['sent', 'overdue']).count()
    
    # Recent data
    recent_invoices = Invoice.objects.order_by('-created_at')[:5]
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    # Chart data - Last 7 days sales
    sales_data = []
    labels = []
    for i in range(7):
        date = today - timedelta(days=i)
        sales = Invoice.objects.filter(
            invoice_date=date,
            status__in=['sent', 'paid']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        sales_data.insert(0, float(sales))
        labels.insert(0, date.strftime('%d/%m'))
    
    # Top products this month
    from django.db.models import Q
    top_products_data = []
    for product in GlassProduct.objects.filter(status='active')[:5]:
        quantity_sold = Invoice.objects.filter(
            invoice_date__gte=this_month,
            status__in=['sent', 'paid'],
            invoiceitem__product=product
        ).aggregate(total=Sum('invoiceitem__quantity'))['total'] or 0
        
        if quantity_sold > 0:
            top_products_data.append({
                'name': product.name,
                'quantity': float(quantity_sold)
            })
    
    # Customer type distribution
    individual_customers = Customer.objects.filter(customer_type='individual', status='active').count()
    commercial_customers = Customer.objects.filter(customer_type='commercial', status='active').count()
    
    # Payment method statistics
    payment_methods = []
    for method, label in Invoice.PAYMENT_METHODS:
        count = Invoice.objects.filter(
            payment_method=method,
            invoice_date__gte=this_month,
            status__in=['sent', 'paid']
        ).count()
        if count > 0:
            payment_methods.append({'method': label, 'count': count})
    
    context = {
        'today_sales': today_sales,
        'month_revenue': month_revenue,
        'total_customers': total_customers,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products[:5],
        'pending_orders': pending_orders,
        'outstanding_invoices': outstanding_invoices,
        'recent_invoices': recent_invoices,
        'recent_orders': recent_orders,
        'sales_chart_data': {
            'labels': labels,
            'data': sales_data
        },
        'top_products': top_products_data,
        'customer_distribution': {
            'individual': individual_customers,
            'commercial': commercial_customers
        },
        'payment_methods': payment_methods,
    }
    
    return render(request, 'dashboard/home.html', context)



@login_required
def reports_dashboard(request):
    """Main reports dashboard page"""
    return render(request, 'dashboard/reports.html')


@login_required
def sales_reports(request):
    """Sales analytics and reports"""
    # Get date range from request
    period = request.GET.get('period', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Set default date range
    today = timezone.now().date()
    if period == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif period == 'month':
        start_date = today.replace(day=1)
        end_date = today
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = today - timedelta(days=30)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = today
    
    # Sales summary
    invoices = Invoice.objects.filter(
        status='paid',
        invoice_date__gte=start_date,
        invoice_date__lte=end_date
    )
    
    sales_summary = {
        'total_revenue': invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'total_invoices': invoices.count(),
        'average_invoice': invoices.aggregate(Avg('total_amount'))['total_amount__avg'] or 0,
        'total_customers': invoices.values('customer').distinct().count(),
    }
    
    # Daily sales for chart
    daily_sales = invoices.extra(
        select={'day': 'date(invoice_date)'}
    ).values('day').annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    ).order_by('day')
    
    # Monthly sales trend
    monthly_sales = invoices.annotate(
        month=TruncMonth('invoice_date')
    ).values('month').annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    ).order_by('month')
    
    # Top products
    top_products = InvoiceItem.objects.filter(
        invoice__status='paid',
        invoice__invoice_date__gte=start_date,
        invoice__invoice_date__lte=end_date
    ).values(
        'product__name',
        'product__code'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('subtotal'),
        total_surface=Sum(F('width') * F('height') / 10000)
    ).order_by('-total_revenue')[:10]
    
    # Top customers
    top_customers = invoices.values(
        'customer__name',
        'customer__id'
    ).annotate(
        total_spent=Sum('total_amount'),
        invoice_count=Count('id')
    ).order_by('-total_spent')[:10]
    
    # Sales by customer type
    customer_type_sales = invoices.values(
        'customer__customer_type'
    ).annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    )
    
    context = {
        'sales_summary': sales_summary,
        'daily_sales': list(daily_sales),
        'monthly_sales': list(monthly_sales),
        'top_products': top_products,
        'top_customers': top_customers,
        'customer_type_sales': customer_type_sales,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'dashboard/reports/sales_reports.html', context)


@login_required
def inventory_reports(request):
    """Inventory analytics and reports"""
    # Stock levels
    products = GlassProduct.objects.filter(status='active')
    
    # Low stock products
    low_stock_products = products.filter(
        stock_quantity__lte=F('minimum_stock')
    ).order_by('stock_quantity')
    
    # Stock valuation
    stock_value_cost = products.aggregate(
        total_cost=Sum(F('stock_quantity') * F('cost_price'))
    )['total_cost'] or 0
    
    stock_value_selling = products.aggregate(
        total_selling=Sum(F('stock_quantity') * F('selling_price'))
    )['total_selling'] or 0
    
    # Product performance
    product_performance = InvoiceItem.objects.filter(
        invoice__status='paid',
        invoice__invoice_date__gte=timezone.now().date() - timedelta(days=90)
    ).values(
        'product__name',
        'product__code',
        'product__stock_quantity'
    ).annotate(
        sold_quantity=Sum('quantity'),
        revenue=Sum('subtotal')
    ).order_by('-sold_quantity')
    
    # Stock by category
    stock_by_category = products.values('glass_type').annotate(
        total_quantity=Sum('stock_quantity'),
        total_value=Sum(F('stock_quantity') * F('selling_price')),
        product_count=Count('id')
    ).order_by('-total_value')
    
    # Stock alerts
    stock_alerts = {
        'out_of_stock': products.filter(stock_quantity=0).count(),
        'low_stock': low_stock_products.count(),
        'good_stock': products.filter(stock_quantity__gt=F('minimum_stock')).count(),
    }
    
    context = {
        'low_stock_products': low_stock_products[:20],
        'stock_value_cost': stock_value_cost,
        'stock_value_selling': stock_value_selling,
        'potential_profit': stock_value_selling - stock_value_cost,
        'product_performance': product_performance[:15],
        'stock_by_category': stock_by_category,
        'stock_alerts': stock_alerts,
        'total_products': products.count(),
    }
    
    return render(request, 'dashboard/reports/inventory_reports.html', context)


@login_required
def financial_reports(request):
    """Financial analytics and reports"""
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    today = timezone.now().date()
    if not start_date:
        start_date = today.replace(day=1)  # First day of current month
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = today
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Revenue analysis
    paid_invoices = Invoice.objects.filter(
        status='paid',
        invoice_date__gte=start_date,
        invoice_date__lte=end_date
    )
    
    # Outstanding invoices
    outstanding_invoices = Invoice.objects.filter(
        status__in=['sent', 'overdue'],
        invoice_date__gte=start_date,
        invoice_date__lte=end_date
    )
    
    # Financial summary
    financial_summary = {
        'total_revenue': paid_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'outstanding_amount': outstanding_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'total_invoices': Invoice.objects.filter(invoice_date__gte=start_date, invoice_date__lte=end_date).count(),
        'paid_invoices': paid_invoices.count(),
        'outstanding_invoices': outstanding_invoices.count(),
    }
    
    # Payment collection rate
    total_invoiced = Invoice.objects.filter(
        invoice_date__gte=start_date,
        invoice_date__lte=end_date
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    if total_invoiced > 0:
        collection_rate = (financial_summary['total_revenue'] / total_invoiced) * 100
    else:
        collection_rate = 0
    
    # Monthly revenue trend
    monthly_revenue_raw = paid_invoices.annotate(
        month=TruncMonth('invoice_date')
    ).values('month').annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    ).order_by('month')

    # Serialize for JavaScript
    monthly_revenue = []
    for item in monthly_revenue_raw:
        monthly_revenue.append({
            'month': item['month'].isoformat() if item['month'] else None,
            'revenue': float(item['revenue']) if item['revenue'] else 0,
            'count': item['count']
        })


    # Profit margins
    invoice_items = InvoiceItem.objects.filter(
        invoice__status='paid',
        invoice__invoice_date__gte=start_date,
        invoice__invoice_date__lte=end_date
    )
    
    profit_analysis = invoice_items.aggregate(
        total_revenue=Sum('subtotal'),
        total_cost=Sum(F('quantity') * F('product__cost_price') * F('width') * F('height') / 10000),
    )
    
    gross_profit = (profit_analysis['total_revenue'] or 0) - (profit_analysis['total_cost'] or 0)
    profit_margin = (gross_profit / (profit_analysis['total_revenue'] or 1)) * 100 if profit_analysis['total_revenue'] else 0
    
    # Overdue invoices
    overdue_invoices = Invoice.objects.filter(
        status__in=['sent', 'overdue'],
        due_date__lt=today
    ).order_by('due_date')
    
    # Then in your context:
    context = {
        'financial_summary': financial_summary,
        'collection_rate': collection_rate,
        'monthly_revenue': monthly_revenue,  # Now properly serialized
        'gross_profit': gross_profit,
        'profit_margin': profit_margin,
        'overdue_invoices': overdue_invoices[:10],
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'dashboard/reports/financial_reports.html', context)


@login_required
def customer_reports(request):
    """Customer analytics and reports"""
    # Customer summary
    customers = Customer.objects.filter(status='active')
    
    # New customers this month
    this_month = timezone.now().date().replace(day=1)
    new_customers = customers.filter(created_at__gte=this_month).count()
    
    # Customer lifetime value
    customer_ltv = Invoice.objects.filter(
        status='paid'
    ).values(
        'customer__name',
        'customer__id',
        'customer__customer_type'
    ).annotate(
        total_spent=Sum('total_amount'),
        invoice_count=Count('id'),
        avg_invoice=Avg('total_amount'),
        first_purchase=Min('invoice_date'),
        last_purchase=Max('invoice_date')
    ).order_by('-total_spent')
    
    # Customer segmentation
    customer_segments = {
        'high_value': customer_ltv.filter(total_spent__gte=50000).count(),
        'medium_value': customer_ltv.filter(total_spent__gte=10000, total_spent__lt=50000).count(),
        'low_value': customer_ltv.filter(total_spent__lt=10000).count(),
    }
    
    # Customer type distribution
    customer_types = customers.values('customer_type').annotate(
        count=Count('id')
    )
    
    # Customer acquisition trend - Convert datetime to string for JavaScript
    from django.db.models.functions import TruncMonth
    customer_acquisition_raw = customers.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        new_customers=Count('id')
    ).order_by('month')
    
    # Convert datetime objects to ISO format strings for JavaScript
    customer_acquisition = []
    for item in customer_acquisition_raw:
        customer_acquisition.append({
            'month': item['month'].isoformat() if item['month'] else None,
            'new_customers': item['new_customers']
        })
    
    # Top customers by revenue
    top_customers = customer_ltv[:15]
    
    # Customer purchase frequency
    purchase_frequency = Invoice.objects.filter(
        status='paid'
    ).values('customer').annotate(
        purchase_count=Count('id')
    ).values('purchase_count').annotate(
        customer_count=Count('customer')
    ).order_by('purchase_count')
    
    context = {
        'total_customers': customers.count(),
        'new_customers': new_customers,
        'customer_segments': customer_segments,
        'customer_types': customer_types,
        'customer_acquisition': customer_acquisition,  # Now properly serialized
        'top_customers': top_customers,
        'purchase_frequency': list(purchase_frequency),
    }
    
    return render(request, 'dashboard/reports/customer_reports.html', context)

@login_required
def export_sales_excel(request):
    """Export sales data to Excel"""
    # Get parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Create Excel file in memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'border': 1
    })
    
    currency_format = workbook.add_format({'num_format': '#,##0.00'})
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    
    # Sales Summary Sheet
    summary_sheet = workbook.add_worksheet('Résumé des Ventes')
    
    invoices = Invoice.objects.filter(
        status='paid',
        invoice_date__gte=start_date,
        invoice_date__lte=end_date
    )
    
    # Write summary data
    summary_sheet.write('A1', 'Rapport de Ventes', header_format)
    summary_sheet.write('A2', f'Période: {start_date} à {end_date}')
    summary_sheet.write('A4', 'Chiffre d\'affaires total:', header_format)
    summary_sheet.write('B4', invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0, currency_format)
    summary_sheet.write('A5', 'Nombre de factures:', header_format)
    summary_sheet.write('B5', invoices.count())
    summary_sheet.write('A6', 'Facture moyenne:', header_format)
    summary_sheet.write('B6', invoices.aggregate(Avg('total_amount'))['total_amount__avg'] or 0, currency_format)
    
    # Detailed Sales Sheet
    details_sheet = workbook.add_worksheet('Détails des Ventes')
    
    headers = ['Numéro Facture', 'Date', 'Client', 'Montant HT', 'TVA', 'Total TTC', 'Statut']
    for col, header in enumerate(headers):
        details_sheet.write(0, col, header, header_format)
    
    for row, invoice in enumerate(invoices, 1):
        details_sheet.write(row, 0, invoice.invoice_number)
        details_sheet.write(row, 1, invoice.invoice_date, date_format)
        details_sheet.write(row, 2, invoice.customer.name)
        details_sheet.write(row, 3, float(invoice.subtotal), currency_format)
        details_sheet.write(row, 4, float(invoice.tax_amount), currency_format)
        details_sheet.write(row, 5, float(invoice.total_amount), currency_format)
        details_sheet.write(row, 6, invoice.get_status_display())
    
    # Adjust column widths
    summary_sheet.set_column('A:B', 20)
    details_sheet.set_column('A:G', 15)
    
    workbook.close()
    output.seek(0)
    
    # Create response
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=ventes_{start_date}_{end_date}.xlsx'
    
    return response


@login_required
def export_inventory_excel(request):
    """Export inventory data to Excel"""
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'border': 1
    })
    
    currency_format = workbook.add_format({'num_format': '#,##0.00'})
    alert_format = workbook.add_format({'bg_color': '#ffcccc'})
    
    # Inventory Sheet
    inventory_sheet = workbook.add_worksheet('Inventaire')
    
    headers = [
        'Code', 'Nom', 'Type', 'Épaisseur', 'Couleur', 'Stock', 'Stock Min',
        'Prix Revient', 'Prix Vente', 'Valeur Stock', 'Statut'
    ]
    
    for col, header in enumerate(headers):
        inventory_sheet.write(0, col, header, header_format)
    
    products = GlassProduct.objects.filter(status='active').order_by('name')
    
    for row, product in enumerate(products, 1):
        # Apply alert format for low stock
        row_format = alert_format if product.is_low_stock() else None
        
        inventory_sheet.write(row, 0, product.code, row_format)
        inventory_sheet.write(row, 1, product.name, row_format)
        inventory_sheet.write(row, 2, product.get_glass_type_display(), row_format)
        inventory_sheet.write(row, 3, f"{product.thickness}mm", row_format)
        inventory_sheet.write(row, 4, product.get_color_display(), row_format)
        inventory_sheet.write(row, 5, float(product.stock_quantity), row_format)
        inventory_sheet.write(row, 6, float(product.minimum_stock), row_format)
        inventory_sheet.write(row, 7, float(product.cost_price), currency_format)
        inventory_sheet.write(row, 8, float(product.selling_price), currency_format)
        inventory_sheet.write(row, 9, float(product.stock_quantity * product.selling_price), currency_format)
        inventory_sheet.write(row, 10, product.get_status_display(), row_format)
    
    # Adjust column widths
    inventory_sheet.set_column('A:K', 12)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=inventaire.xlsx'
    
    return response


@login_required
def export_customers_csv(request):
    """Export customers data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=clients.csv'
    
    writer = csv.writer(response)
    writer.writerow([
        'Nom', 'Type', 'Téléphone', 'Email', 'Adresse', 'Total Achats', 
        'Nombre Factures', 'Dernière Commande', 'Statut'
    ])
    
    # Get customer data with aggregated purchase info
    customers = Customer.objects.annotate(
        total_purchases=Sum('invoice__total_amount'),
        invoice_count=Count('invoice'),
        last_purchase=Max('invoice__invoice_date')
    ).order_by('name')
    
    for customer in customers:
        writer.writerow([
            customer.name,
            customer.get_customer_type_display(),
            customer.phone,
            customer.email,
            customer.address.replace('\n', ' '),
            customer.total_purchases or 0,
            customer.invoice_count or 0,
            customer.last_purchase.strftime('%d/%m/%Y') if customer.last_purchase else 'Jamais',
            customer.get_status_display()
        ])
    
    return response


@login_required
def export_financial_pdf(request):
    """Export financial report to PDF"""
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    today = timezone.now().date()
    if not start_date:
        start_date = today.replace(day=1)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = today
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Get company info
    company = Company.objects.first()
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Content
    story = []
    
    # Title
    story.append(Paragraph("Rapport Financier", title_style))
    if company:
        story.append(Paragraph(f"<b>{company.name}</b>", styles['Normal']))
    story.append(Paragraph(f"Période: {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Financial data
    paid_invoices = Invoice.objects.filter(
        status='paid',
        invoice_date__gte=start_date,
        invoice_date__lte=end_date
    )
    
    outstanding_invoices = Invoice.objects.filter(
        status__in=['sent', 'overdue'],
        invoice_date__gte=start_date,
        invoice_date__lte=end_date
    )
    
    total_revenue = paid_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    outstanding_amount = outstanding_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Summary table
    summary_data = [
        ['Indicateur', 'Valeur'],
        ['Chiffre d\'affaires', f'{total_revenue:,.2f} DA'],
        ['Créances en cours', f'{outstanding_amount:,.2f} DA'],
        ['Factures payées', str(paid_invoices.count())],
        ['Factures en attente', str(outstanding_invoices.count())],
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    
    # Build PDF
    doc.build(story)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=rapport_financier_{start_date}_{end_date}.pdf'
    
    return response


@login_required
def dashboard_api_data(request):
    """API endpoint for dashboard charts data"""
    data_type = request.GET.get('type', 'sales')
    
    if data_type == 'sales':
        # Monthly sales for the last 12 months
        twelve_months_ago = timezone.now().date() - timedelta(days=365)
        monthly_sales = Invoice.objects.filter(
            status='paid',
            invoice_date__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('invoice_date')
        ).values('month').annotate(
            revenue=Sum('total_amount')
        ).order_by('month')
        
        return JsonResponse({
            'labels': [item['month'].strftime('%b %Y') for item in monthly_sales],
            'data': [float(item['revenue']) for item in monthly_sales]
        })
    
    elif data_type == 'products':
        # Top 10 products by revenue
        top_products = InvoiceItem.objects.filter(
            invoice__status='paid'
        ).values('product__name').annotate(
            revenue=Sum('subtotal')
        ).order_by('-revenue')[:10]
        
        return JsonResponse({
            'labels': [item['product__name'] for item in top_products],
            'data': [float(item['revenue']) for item in top_products]
        })
    
    elif data_type == 'customers':
        # Customer type distribution
        customer_types = Invoice.objects.filter(
            status='paid'
        ).values('customer__customer_type').annotate(
            revenue=Sum('total_amount')
        )
        
        return JsonResponse({
            'labels': [Customer.CUSTOMER_TYPES[i][1] for i in range(len(Customer.CUSTOMER_TYPES))],
            'data': [float(item['revenue']) for item in customer_types]
        })
    
    return JsonResponse({'error': 'Invalid data type'}, status=400)



