from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Supplier
from .forms import SupplierForm

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        suppliers = suppliers.filter(name__icontains=search)
    
    # Pagination
    paginator = Paginator(suppliers, 10)
    page_number = request.GET.get('page')
    suppliers = paginator.get_page(page_number)
    
    return render(request, 'suppliers/list.html', {'suppliers': suppliers, 'search': search})

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