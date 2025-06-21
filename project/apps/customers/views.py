from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from datetime import datetime
from .models import Customer
from .forms import CustomerForm

@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    
    # Text search functionality (name, email, phone)
    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Filter by customer type
    customer_type = request.GET.get('customer_type')
    if customer_type:
        customers = customers.filter(customer_type=customer_type)
    
    # Filter by creation date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            customers = customers.filter(created_at__date__gte=date_from_parsed)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            customers = customers.filter(created_at__date__lte=date_to_parsed)
        except ValueError:
            pass
    
    # Filter by total purchases range
    min_purchases = request.GET.get('min_purchases')
    max_purchases = request.GET.get('max_purchases')
    
    if min_purchases or max_purchases:
        # Annotate customers with their total purchases
        from apps.invoices.models import Invoice
        customers = customers.annotate(
            total_purchases=Sum('invoice__total_amount')
        )
        
        if min_purchases:
            try:
                min_val = float(min_purchases)
                customers = customers.filter(total_purchases__gte=min_val)
            except (ValueError, TypeError):
                pass
        
        if max_purchases:
            try:
                max_val = float(max_purchases)
                customers = customers.filter(total_purchases__lte=max_val)
            except (ValueError, TypeError):
                pass
    
    # Pagination
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)
    
    # Prepare filter context
    filter_context = {
        'search': search,
        'customer_type': customer_type,
        'date_from': date_from,
        'date_to': date_to,
        'min_purchases': min_purchases,
        'max_purchases': max_purchases,
        'customer_types': Customer.CUSTOMER_TYPES,
    }
    
    return render(request, 'customers/list.html', {
        'customers': customers,
        'filters': filter_context
    })

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Client {customer.name} créé avec succès.')
            return redirect('customers:list')
    else:
        form = CustomerForm()
    
    return render(request, 'customers/form.html', {'form': form, 'title': 'Nouveau Client'})

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client {customer.name} modifié avec succès.')
            return redirect('customers:list')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customers/form.html', {'form': form, 'title': 'Modifier Client', 'customer': customer})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customers/detail.html', {'customer': customer})

@login_required
def customer_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Vous n\'avez pas les permissions pour supprimer un client.')
        return redirect('customers:list')
    
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, f'Client {customer.name} supprimé avec succès.')
        return redirect('customers:list')
    
    return render(request, 'customers/delete.html', {'customer': customer})