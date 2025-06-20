from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from apps.invoices.models import Invoice, Payment
from apps.customers.models import Customer
from apps.orders.models import Order
from apps.inventory.models import GlassProduct

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
def reports_view(request):
    # This could be expanded for detailed reports
    return render(request, 'dashboard/reports.html')