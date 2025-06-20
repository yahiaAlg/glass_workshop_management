from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.http import HttpResponse
from .models import Invoice, InvoiceItem, InvoiceService, Payment
from .forms import InvoiceForm, InvoiceItemForm, InvoiceServiceForm, PaymentForm

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        invoices = invoices.filter(invoice_number__icontains=search)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        invoices = invoices.filter(status=status)
    
    # Pagination
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)
    
    return render(request, 'invoices/list.html', {
        'invoices': invoices, 
        'search': search,
        'status': status,
        'status_choices': Invoice.STATUS_CHOICES
    })

@login_required
def invoice_create(request):
    InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True)
    InvoiceServiceFormSet = inlineformset_factory(Invoice, InvoiceService, form=InvoiceServiceForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        item_formset = InvoiceItemFormSet(request.POST, prefix='items')
        service_formset = InvoiceServiceFormSet(request.POST, prefix='services')
        
        if form.is_valid() and item_formset.is_valid() and service_formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            
            item_formset.instance = invoice
            item_formset.save()
            
            service_formset.instance = invoice
            service_formset.save()
            
            invoice.calculate_totals()
            messages.success(request, f'Facture {invoice.invoice_number} créée avec succès.')
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        item_formset = InvoiceItemFormSet(prefix='items')
        service_formset = InvoiceServiceFormSet(prefix='services')
    
    return render(request, 'invoices/form.html', {
        'form': form, 
        'item_formset': item_formset,
        'service_formset': service_formset,
        'title': 'Nouvelle Facture'
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