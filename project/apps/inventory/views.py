from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import GlassProduct
from .forms import GlassProductForm

@login_required
def product_list(request):
    products = GlassProduct.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(glass_type__icontains=search)
        )
    
    # Filter by low stock
    low_stock = request.GET.get('low_stock')
    if low_stock:
        products = [p for p in products if p.is_low_stock()]
    
    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    return render(request, 'inventory/list.html', {
        'products': products, 
        'search': search,
        'low_stock': low_stock
    })

@login_required
def product_create(request):
    if request.method == 'POST':
        form = GlassProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Produit {product.name} créé avec succès.')
            return redirect('inventory:list')
    else:
        form = GlassProductForm()
    
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Nouveau Produit'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(GlassProduct, pk=pk)
    
    if request.method == 'POST':
        form = GlassProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produit {product.name} modifié avec succès.')
            return redirect('inventory:list')
    else:
        form = GlassProductForm(instance=product)
    
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Modifier Produit', 'product': product})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(GlassProduct, pk=pk)
    return render(request, 'inventory/detail.html', {'product': product})

@login_required
def product_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Vous n\'avez pas les permissions pour supprimer un produit.')
        return redirect('inventory:list')
    
    product = get_object_or_404(GlassProduct, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Produit {product.name} supprimé avec succès.')
        return redirect('inventory:list')
    
    return render(request, 'inventory/delete.html', {'product': product})

@login_required
def low_stock_alert(request):
    low_stock_products = [p for p in GlassProduct.objects.filter(status='active') if p.is_low_stock()]
    return render(request, 'inventory/low_stock.html', {'products': low_stock_products})