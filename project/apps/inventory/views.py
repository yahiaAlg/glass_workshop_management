from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import *
from .forms import *

@login_required
def product_list(request):
    products = GlassProduct.objects.all().order_by('-created_at')
    
    # Search functionality - search by code and name
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search)
        )
    
    # Filter by supplier
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        products = products.filter(supplier_id=supplier_id)
    
    # Filter by glass type
    glass_type = request.GET.get('glass_type')
    if glass_type:
        products = products.filter(glass_type=glass_type)
    
    # Filter by thickness
    thickness = request.GET.get('thickness')
    if thickness:
        products = products.filter(thickness=thickness)
    
    # Filter by unit of measure
    unit = request.GET.get('unit')
    if unit:
        products = products.filter(unit=unit)
    
    # Filter by selling price range
    min_selling_price = request.GET.get('min_selling_price')
    max_selling_price = request.GET.get('max_selling_price')
    if min_selling_price:
        try:
            products = products.filter(selling_price__gte=float(min_selling_price))
        except ValueError:
            pass
    if max_selling_price:
        try:
            products = products.filter(selling_price__lte=float(max_selling_price))
        except ValueError:
            pass
    
    # Filter by cost price range
    min_cost_price = request.GET.get('min_cost_price')
    max_cost_price = request.GET.get('max_cost_price')
    if min_cost_price:
        try:
            products = products.filter(cost_price__gte=float(min_cost_price))
        except ValueError:
            pass
    if max_cost_price:
        try:
            products = products.filter(cost_price__lte=float(max_cost_price))
        except ValueError:
            pass
    
    # Filter by stock quantity range
    min_stock = request.GET.get('min_stock')
    max_stock = request.GET.get('max_stock')
    if min_stock:
        try:
            products = products.filter(stock_quantity__gte=float(min_stock))
        except ValueError:
            pass
    if max_stock:
        try:
            products = products.filter(stock_quantity__lte=float(max_stock))
        except ValueError:
            pass
    
    # Filter by low stock
    low_stock = request.GET.get('low_stock')
    if low_stock:
        # Convert to list to use is_low_stock method
        products_list = list(products)
        products_list = [p for p in products_list if p.is_low_stock()]
        
        # Create a paginator with the filtered list
        paginator = Paginator(products_list, 10)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)
    else:
        # Standard pagination
        paginator = Paginator(products, 10)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)
    
    # Get choices for filter dropdowns
    glass_types = GlassType.objects.filter(is_active=True)
    thickness_choices = GlassThickness.objects.filter(is_active=True)
    unit_choices = Unit.objects.filter(is_active=True)
    
    # Get supplier name if filtering by supplier
    supplier_name = None
    if supplier_id:
        try:
            from apps.suppliers.models import Supplier
            supplier = Supplier.objects.get(pk=supplier_id)
            supplier_name = supplier.name
        except (ImportError, Supplier.DoesNotExist):
            pass
    
    context = {
        'products': products,
        'search': search,
        'supplier_id': supplier_id,
        'supplier_name': supplier_name,
        'glass_type': glass_type,
        'thickness': thickness,
        'unit': unit,
        'min_selling_price': min_selling_price,
        'max_selling_price': max_selling_price,
        'min_cost_price': min_cost_price,
        'max_cost_price': max_cost_price,
        'min_stock': min_stock,
        'max_stock': max_stock,
        'low_stock': low_stock,
        'glass_types': glass_types,
        'thickness_choices': thickness_choices,
        'unit_choices': unit_choices,
    }
    
    return render(request, 'inventory/list.html', context)

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

@login_required
def products_api(request):
    """API endpoint to return products data for AJAX requests"""
    products = GlassProduct.objects.filter(status='active').select_related(
        'glass_type', 'thickness', 'unit', 'color', 'finish'
    )
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product.id,
            'name': product.name,
            'selling_price': float(product.selling_price),
            'thickness': product.thickness.display_name,
            'unit': product.unit.name,
            'color': product.color.name,
            'glass_type': product.glass_type.name,
            'finish': product.finish.name
        })
    
    return JsonResponse(products_list, safe=False)