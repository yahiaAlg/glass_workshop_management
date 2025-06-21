from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.db.models import Q
from datetime import datetime
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm

@login_required
def order_list(request):
    orders = Order.objects.select_related('customer').all().order_by('-created_at')
    
    # Text search functionality (order number and customer name)
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) | 
            Q(customer__name__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Filter by order date range
    order_date_from = request.GET.get('order_date_from')
    order_date_to = request.GET.get('order_date_to')
    if order_date_from:
        try:
            date_from = datetime.strptime(order_date_from, '%Y-%m-%d').date()
            orders = orders.filter(order_date__date__gte=date_from)
        except ValueError:
            messages.warning(request, 'Format de date invalide pour la date de début.')
    
    if order_date_to:
        try:
            date_to = datetime.strptime(order_date_to, '%Y-%m-%d').date()
            orders = orders.filter(order_date__date__lte=date_to)
        except ValueError:
            messages.warning(request, 'Format de date invalide pour la date de fin.')
    
    # Filter by delivery date range
    delivery_date_from = request.GET.get('delivery_date_from')
    delivery_date_to = request.GET.get('delivery_date_to')
    if delivery_date_from:
        try:
            date_from = datetime.strptime(delivery_date_from, '%Y-%m-%d').date()
            orders = orders.filter(delivery_date__gte=date_from)
        except ValueError:
            messages.warning(request, 'Format de date invalide pour la date de livraison début.')
    
    if delivery_date_to:
        try:
            date_to = datetime.strptime(delivery_date_to, '%Y-%m-%d').date()
            orders = orders.filter(delivery_date__lte=date_to)
        except ValueError:
            messages.warning(request, 'Format de date invalide pour la date de livraison fin.')
    
    # Filter by total amount range
    amount_min = request.GET.get('amount_min')
    amount_max = request.GET.get('amount_max')
    if amount_min:
        try:
            min_amount = float(amount_min)
            orders = orders.filter(total_amount__gte=min_amount)
        except ValueError:
            messages.warning(request, 'Montant minimum invalide.')
    
    if amount_max:
        try:
            max_amount = float(amount_max)
            orders = orders.filter(total_amount__lte=max_amount)
        except ValueError:
            messages.warning(request, 'Montant maximum invalide.')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    return render(request, 'orders/list.html', {
        'orders': orders, 
        'search': search,
        'status': status,
        'order_date_from': order_date_from,
        'order_date_to': order_date_to,
        'delivery_date_from': delivery_date_from,
        'delivery_date_to': delivery_date_to,
        'amount_min': amount_min,
        'amount_max': amount_max,
        'status_choices': Order.STATUS_CHOICES
    })

@login_required
def order_create(request):
    OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True)
    
    # Get customer from query parameter for prepopulation
    customer_id = request.GET.get('customer_id')
    customer = None
    if customer_id:
        try:
            from apps.customers.models import Customer
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            messages.error(request, 'Client introuvable.')
            return redirect('orders:list')
    
    # Get product from query parameter for prepopulation
    product_id = request.GET.get('product')
    product = None
    if product_id:
        try:
            from apps.inventory.models import GlassProduct
            product = GlassProduct.objects.get(pk=product_id)
        except GlassProduct.DoesNotExist:
            messages.error(request, 'Produit introuvable.')
            return redirect('orders:list')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            order.calculate_total()
            messages.success(request, f'Commande {order.order_number} créée avec succès.')
            return redirect('orders:detail', pk=order.pk)
    else:
        # Prepopulate form with customer data
        initial_data = {}
        if customer:
            initial_data = {
                'customer': customer,
                'delivery_address': customer.address,
            }
        
        form = OrderForm(initial=initial_data)
        
        # Prepopulate item formset with single product
        if product:
            item_initial_data = [{
                'product': product,
                'quantity': 1,
                'unit_price': product.selling_price,
                'width': 100,  # Default width in cm
                'height': 100,  # Default height in cm
            }]
            
            formset = OrderItemFormSet(initial=item_initial_data)
        else:
            formset = OrderItemFormSet()
    
    return render(request, 'orders/form.html', {
        'form': form, 
        'formset': formset, 
        'title': 'Nouvelle Commande',
        'customer': customer,  # Pass customer to template for reference
        'product': product,  # Pass product to template for reference
    })


@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=0, can_delete=True)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            order.calculate_total()
            messages.success(request, f'Commande {order.order_number} modifiée avec succès.')
            return redirect('orders:detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)
    
    return render(request, 'orders/form.html', {
        'form': form, 
        'formset': formset, 
        'title': 'Modifier Commande',
        'order': order
    })

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.orderitem_set.all()
    return render(request, 'orders/detail.html', {'order': order, 'items': items})

@login_required
def order_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Vous n\'avez pas les permissions pour supprimer une commande.')
        return redirect('orders:list')
    
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'Commande {order.order_number} supprimée avec succès.')
        return redirect('orders:list')
    
    return render(request, 'orders/delete.html', {'order': order})