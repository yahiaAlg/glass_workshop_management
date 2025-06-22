from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.db.models import Q
from datetime import datetime

from apps.orders.models import Order
from .models import Invoice, InvoiceItem, InvoiceService
from .forms import InvoiceForm, InvoiceItemForm, InvoiceServiceForm, PaymentForm

@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('customer').all().order_by('-created_at')
    
    # Text search functionality (invoice number and customer name)
    search = request.GET.get('search')
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) | 
            Q(customer__name__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        invoices = invoices.filter(status=status)
    
    # Filter by invoice date range
    invoice_date_from = request.GET.get('invoice_date_from')
    invoice_date_to = request.GET.get('invoice_date_to')
    if invoice_date_from:
        try:
            date_from = datetime.strptime(invoice_date_from, '%Y-%m-%d').date()
            invoices = invoices.filter(invoice_date__gte=date_from)
        except ValueError:
            pass
    if invoice_date_to:
        try:
            date_to = datetime.strptime(invoice_date_to, '%Y-%m-%d').date()
            invoices = invoices.filter(invoice_date__lte=date_to)
        except ValueError:
            pass
    
    # Filter by due date range
    due_date_from = request.GET.get('due_date_from')
    due_date_to = request.GET.get('due_date_to')
    if due_date_from:
        try:
            date_from = datetime.strptime(due_date_from, '%Y-%m-%d').date()
            invoices = invoices.filter(due_date__gte=date_from)
        except ValueError:
            pass
    if due_date_to:
        try:
            date_to = datetime.strptime(due_date_to, '%Y-%m-%d').date()
            invoices = invoices.filter(due_date__lte=date_to)
        except ValueError:
            pass
    
    # Filter by total amount range
    amount_min = request.GET.get('amount_min')
    amount_max = request.GET.get('amount_max')
    if amount_min:
        try:
            min_amount = float(amount_min)
            invoices = invoices.filter(total_amount__gte=min_amount)
        except ValueError:
            pass
    if amount_max:
        try:
            max_amount = float(amount_max)
            invoices = invoices.filter(total_amount__lte=max_amount)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)
    
    return render(request, 'invoices/list.html', {
        'invoices': invoices, 
        'search': search,
        'status': status,
        'invoice_date_from': invoice_date_from,
        'invoice_date_to': invoice_date_to,
        'due_date_from': due_date_from,
        'due_date_to': due_date_to,
        'amount_min': amount_min,
        'amount_max': amount_max,
        'status_choices': Invoice.STATUS_CHOICES
    })


@login_required
def invoice_create(request):
    InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True)
    InvoiceServiceFormSet = inlineformset_factory(Invoice, InvoiceService, form=InvoiceServiceForm, extra=1, can_delete=True)
    
    # Get order from query parameter for prepopulation
    order_id = request.GET.get('order_id')
    order = None
    if order_id:
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            messages.error(request, 'Commande introuvable.')
            return redirect('invoices:list')
    
    # Get customer from query parameter for prepopulation
    customer_id = request.GET.get('customer_id')
    customer = None
    if customer_id:
        try:
            from apps.customers.models import Customer
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            messages.error(request, 'Client introuvable.')
            return redirect('invoices:list')
    
    # Get product from query parameter for prepopulation
    product_id = request.GET.get('product')
    product = None
    if product_id:
        try:
            from apps.inventory.models import GlassProduct
            product = GlassProduct.objects.get(pk=product_id)
        except GlassProduct.DoesNotExist:
            messages.error(request, 'Produit introuvable.')
            return redirect('invoices:list')
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        item_formset = InvoiceItemFormSet(request.POST, prefix='items')
        service_formset = InvoiceServiceFormSet(request.POST, prefix='services')
        
        if form.is_valid() and item_formset.is_valid() and service_formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            # Link to order if provided
            if order:
                invoice.order = order
            invoice.save()
            
            item_formset.instance = invoice
            item_formset.save()
            
            service_formset.instance = invoice
            service_formset.save()
            
            invoice.calculate_totals()
            messages.success(request, f'Facture {invoice.invoice_number} créée avec succès.')
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        # Prepopulate form with order or customer data
        initial_data = {}
        if order:
            initial_data = {
                'customer': order.customer,
                'delivery_address': order.delivery_address,
                'delivery_date': order.delivery_date,
                'notes': order.notes,
            }
        elif customer:
            initial_data = {
                'customer': customer,
                'delivery_address': customer.address,
            }
        
        form = InvoiceForm(initial=initial_data)
        
        # Prepopulate item formset with order items
        if order and order.orderitem_set.exists():
            # Create initial data for items based on order items
            item_initial_data = []
            for order_item in order.orderitem_set.all():
                item_initial_data.append({
                    'product': order_item.product,
                    'description': f"{order_item.product.name} - {order_item.width}x{order_item.height}cm",
                    'quantity': order_item.quantity,
                    'unit_price': order_item.unit_price,
                    'width': order_item.width,
                    'height': order_item.height,
                    'thickness': getattr(order_item.product, 'thickness', ''),
                })
            
            item_formset = InvoiceItemFormSet(prefix='items', initial=item_initial_data)
            # Add installation service if required
            service_initial_data = []
            if order.installation_required:
                service_initial_data.append({
                    'service_type': 'installation',
                    'description': 'Installation sur site',
                    'amount': 0,  # You can set a default installation fee
                })
            
            service_formset = InvoiceServiceFormSet(prefix='services', initial=service_initial_data)
        # Prepopulate item formset with single product
        elif product:
            item_initial_data = [{
                'product': product,
                'description': f"{product.name} - {product.get_thickness_display()} {product.get_color_display()}",
                'quantity': 1,
                'unit_price': product.selling_price,
                'thickness': product.thickness,
            }]
            
            item_formset = InvoiceItemFormSet(prefix='items', initial=item_initial_data)
            service_formset = InvoiceServiceFormSet(prefix='services')
        else:
            item_formset = InvoiceItemFormSet(prefix='items')
            service_formset = InvoiceServiceFormSet(prefix='services')
    
    return render(request, 'invoices/form.html', {
        'form': form, 
        'item_formset': item_formset,
        'service_formset': service_formset,
        'title': 'Nouvelle Facture',
        'order': order,  # Pass order to template for reference
        'customer': customer,  # Pass customer to template for reference
        'product': product,  # Pass product to template for reference
    })
    
        
@login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=0, can_delete=True)
    InvoiceServiceFormSet = inlineformset_factory(Invoice, InvoiceService, form=InvoiceServiceForm, extra=0, can_delete=True)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        item_formset = InvoiceItemFormSet(request.POST, instance=invoice, prefix='items')
        service_formset = InvoiceServiceFormSet(request.POST, instance=invoice, prefix='services')
        
        if form.is_valid() and item_formset.is_valid() and service_formset.is_valid():
            form.save()
            item_formset.save()
            service_formset.save()
            invoice.calculate_totals()
            messages.success(request, f'Facture {invoice.invoice_number} modifiée avec succès.')
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        item_formset = InvoiceItemFormSet(instance=invoice, prefix='items')
        service_formset = InvoiceServiceFormSet(instance=invoice, prefix='services')
    
    return render(request, 'invoices/form.html', {
        'form': form, 
        'item_formset': item_formset,
        'service_formset': service_formset,
        'title': 'Modifier Facture',
        'invoice': invoice
    })

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.invoiceitem_set.all()
    services = invoice.invoiceservice_set.all()
    payments = invoice.payment_set.all()
    return render(request, 'invoices/detail.html', {
        'invoice': invoice, 
        'items': items, 
        'services': services,
        'payments': payments
    })

@login_required
def invoice_print(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.invoiceitem_set.all()
    services = invoice.invoiceservice_set.all()
    return render(request, 'invoices/print.html', {
        'invoice': invoice, 
        'items': items, 
        'services': services
    })

@login_required
def invoice_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Vous n\'avez pas les permissions pour supprimer une facture.')
        return redirect('invoices:list')
    
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, f'Facture {invoice.invoice_number} supprimée avec succès.')
        return redirect('invoices:list')
    
    return render(request, 'invoices/delete.html', {'invoice': invoice})

@login_required
def add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.save()
            
            # Update invoice status if fully paid
            total_payments = sum(p.amount for p in invoice.payment_set.filter(status='completed'))
            if total_payments >= invoice.total_amount:
                invoice.status = 'paid'
                invoice.save()
            
            messages.success(request, 'Paiement enregistré avec succès.')
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        form = PaymentForm(initial={'amount': invoice.total_amount})
    
    return render(request, 'invoices/add_payment.html', {'form': form, 'invoice': invoice})

