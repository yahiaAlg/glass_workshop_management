from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Supplier
from .forms import SupplierForm

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-created_at')
    
    # Enhanced search functionality
    search = request.GET.get('search')
    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(address__icontains=search)
        )
    
    # Payment terms filter
    payment_terms = request.GET.get('payment_terms')
    if payment_terms:
        suppliers = suppliers.filter(payment_terms__icontains=payment_terms)
    
    # Last order date filter
    last_order_from = request.GET.get('last_order_from')
    last_order_to = request.GET.get('last_order_to')
    
    if last_order_from:
        try:
            from_date = datetime.strptime(last_order_from, '%Y-%m-%d').date()
            suppliers = suppliers.filter(last_order_date__gte=from_date)
        except ValueError:
            pass
    
    if last_order_to:
        try:
            to_date = datetime.strptime(last_order_to, '%Y-%m-%d').date()
            suppliers = suppliers.filter(last_order_date__lte=to_date)
        except ValueError:
            pass
    
    # Status filter
    status = request.GET.get('status')
    if status:
        suppliers = suppliers.filter(status=status)
    
    # Get unique payment terms for filter dropdown
    payment_terms_choices = Supplier.objects.values_list('payment_terms', flat=True).distinct().order_by('payment_terms')
    
    # Pagination
    paginator = Paginator(suppliers, 10)
    page_number = request.GET.get('page')
    suppliers = paginator.get_page(page_number)
    
    context = {
        'suppliers': suppliers,
        'search': search,
        'payment_terms': payment_terms,
        'last_order_from': last_order_from,
        'last_order_to': last_order_to,
        'status': status,
        'payment_terms_choices': payment_terms_choices,
        'status_choices': Supplier.STATUS_CHOICES,
    }
    
    return render(request, 'suppliers/list.html', context)

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Fournisseur {supplier.name} créé avec succès.')
            return redirect('suppliers:list')
    else:
        form = SupplierForm()
    
    return render(request, 'suppliers/form.html', {'form': form, 'title': 'Nouveau Fournisseur'})

@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fournisseur {supplier.name} modifié avec succès.')
            return redirect('suppliers:list')
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'suppliers/form.html', {'form': form, 'title': 'Modifier Fournisseur', 'supplier': supplier})

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'suppliers/detail.html', {'supplier': supplier})

@login_required
def supplier_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Vous n\'avez pas les permissions pour supprimer un fournisseur.')
        return redirect('suppliers:list')
    
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, f'Fournisseur {supplier.name} supprimé avec succès.')
        return redirect('suppliers:list')
    
    return render(request, 'suppliers/delete.html', {'supplier': supplier})