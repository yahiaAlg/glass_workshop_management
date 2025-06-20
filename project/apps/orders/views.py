from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm

@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        orders = orders.filter(order_number__icontains=search)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    return render(request, 'orders/list.html', {
        'orders': orders, 
        'search': search,
        'status': status,
        'status_choices': Order.STATUS_CHOICES
    })

@login_required
def order_create(request):
    OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True)
    
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
        form = OrderForm()
        formset = OrderItemFormSet()
    
    return render(request, 'orders/form.html', {
        'form': form, 
        'formset': formset, 
        'title': 'Nouvelle Commande'
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