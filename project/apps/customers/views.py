from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Customer
from .forms import CustomerForm

@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        customers = customers.filter(name__icontains=search)
    
    # Pagination
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)
    
    return render(request, 'customers/list.html', {'customers': customers, 'search': search})

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