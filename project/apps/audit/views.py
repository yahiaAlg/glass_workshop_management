from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import *
from .forms import *

@login_required
def expense_list(request):
    expenses = AdditionalExpense.objects.all()
    
    # Filtres
    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if category_filter:
        expenses = expenses.filter(category__name=category_filter)
    if status_filter:
        expenses = expenses.filter(status=status_filter)
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    if search:
        expenses = expenses.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(vendor__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'page_obj': page_obj,
        'categories': ExpenseCategory.objects.filter(is_active=True),
        'total_amount': total_amount,
        'filters': {
            'category': category_filter,
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to,
            'search': search,
        }
    }
    return render(request, 'audit/expense_list.html', context)

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = AdditionalExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, 'Dépense créée avec succès.')
            return redirect('audit:expense_detail', pk=expense.pk)
    else:
        form = AdditionalExpenseForm()
    
    return render(request, 'audit/expense_form.html', {'form': form, 'title': 'Nouvelle Dépense'})

@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(AdditionalExpense, pk=pk)
    documents = expense.documents.all()
    
    return render(request, 'audit/expense_detail.html', {
        'expense': expense,
        'documents': documents
    })

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(AdditionalExpense, pk=pk)
    
    if request.method == 'POST':
        form = AdditionalExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dépense mise à jour avec succès.')
            return redirect('audit:expense_detail', pk=expense.pk)
    else:
        form = AdditionalExpenseForm(instance=expense)
    
    return render(request, 'audit/expense_form.html', {
        'form': form, 
        'expense': expense,
        'title': 'Modifier Dépense'
    })

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(AdditionalExpense, pk=pk)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Dépense supprimée avec succès.')
        return redirect('audit:expense_list')
    
    return render(request, 'audit/expense_confirm_delete.html', {'expense': expense})

# Revenue CRUD operations
@login_required
def revenue_list(request):
    revenues = AdditionalRevenue.objects.all()
    
    # Filtres similaires aux dépenses
    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if category_filter:
        revenues = revenues.filter(category__name=category_filter)
    if status_filter:
        revenues = revenues.filter(status=status_filter)
    if date_from:
        revenues = revenues.filter(date__gte=date_from)
    if date_to:
        revenues = revenues.filter(date__lte=date_to)
    if search:
        revenues = revenues.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(client__icontains=search)
        )
    
    paginator = Paginator(revenues, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    total_amount = revenues.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'page_obj': page_obj,
        'categories': RevenueCategory.objects.filter(is_active=True),
        'total_amount': total_amount,
        'filters': {
            'category': category_filter,
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to,
            'search': search,
        }
    }
    return render(request, 'audit/revenue_list.html', context)

@login_required
def revenue_create(request):
    if request.method == 'POST':
        form = AdditionalRevenueForm(request.POST)
        if form.is_valid():
            revenue = form.save(commit=False)
            revenue.created_by = request.user
            revenue.save()
            messages.success(request, 'Revenu créé avec succès.')
            return redirect('audit:revenue_detail', pk=revenue.pk)
    else:
        form = AdditionalRevenueForm()
    
    return render(request, 'audit/revenue_form.html', {'form': form, 'title': 'Nouveau Revenu'})

@login_required
def revenue_detail(request, pk):
    revenue = get_object_or_404(AdditionalRevenue, pk=pk)
    documents = revenue.documents.all()
    
    return render(request, 'audit/revenue_detail.html', {
        'revenue': revenue,
        'documents': documents
    })

@login_required
def revenue_update(request, pk):
    revenue = get_object_or_404(AdditionalRevenue, pk=pk)
    
    if request.method == 'POST':
        form = AdditionalRevenueForm(request.POST, instance=revenue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Revenu mis à jour avec succès.')
            return redirect('audit:revenue_detail', pk=revenue.pk)
    else:
        form = AdditionalRevenueForm(instance=revenue)
    
    return render(request, 'audit/revenue_form.html', {
        'form': form, 
        'revenue': revenue,
        'title': 'Modifier Revenu'
    })

@login_required
def revenue_delete(request, pk):
    revenue = get_object_or_404(AdditionalRevenue, pk=pk)
    
    if request.method == 'POST':
        revenue.delete()
        messages.success(request, 'Revenu supprimé avec succès.')
        return redirect('audit:revenue_list')
    
    return render(request, 'audit/revenue_confirm_delete.html', {'revenue': revenue})

@login_required
def dashboard(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Statistiques des dépenses
    total_expenses = AdditionalExpense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expenses = AdditionalExpense.objects.filter(
        date__gte=thirty_days_ago
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Statistiques des revenus
    total_revenues = AdditionalRevenue.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_revenues = AdditionalRevenue.objects.filter(
        date__gte=thirty_days_ago
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Données pour les graphiques
    expense_by_category = AdditionalExpense.objects.values(
        'category__name'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    revenue_by_category = AdditionalRevenue.objects.values(
        'category__name'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'total_expenses': total_expenses,
        'monthly_expenses': monthly_expenses,
        'total_revenues': total_revenues,
        'monthly_revenues': monthly_revenues,
        'net_profit': total_revenues - total_expenses,
        'monthly_net_profit': monthly_revenues - monthly_expenses,
        'expense_by_category': expense_by_category,
        'revenue_by_category': revenue_by_category,
        'recent_expenses': AdditionalExpense.objects.order_by('-created_at')[:5],
        'recent_revenues': AdditionalRevenue.objects.order_by('-created_at')[:5],
    }
    
    return render(request, 'audit/dashboard.html', context)

@login_required
def upload_document(request, type, pk):
    if type == 'expense':
        obj = get_object_or_404(AdditionalExpense, pk=pk)
        DocumentModel = ExpenseDocument
        form_class = ExpenseDocumentForm
    else:
        obj = get_object_or_404(AdditionalRevenue, pk=pk)
        DocumentModel = RevenueDocument
        form_class = RevenueDocumentForm
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            if type == 'expense':
                document.expense = obj
            else:
                document.revenue = obj
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploadé avec succès.')
            return redirect(f'audit:{type}_detail', pk=obj.pk)
    else:
        form = form_class()
    
    return render(request, 'audit/upload_document.html', {
        'form': form,
        'object': obj,
        'type': type
    })

# API endpoints for chart data
@login_required
def expense_chart_data(request):
    # Données pour graphique en secteurs par catégorie
    category_data = AdditionalExpense.objects.values(
        'category__name'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Données pour graphique temporel (6 derniers mois)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    monthly_data = []
    
    for i in range(6):
        month_start = six_months_ago + timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        monthly_total = AdditionalExpense.objects.filter(
            date__gte=month_start,
            date__lt=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'total': float(monthly_total)
        })
    
    # Données par statut
    status_data = AdditionalExpense.objects.values(
        'status'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    return JsonResponse({
        'category_chart': {
            'labels': [item['category__name'] for item in category_data],
            'data': [float(item['total']) for item in category_data],
            'counts': [item['count'] for item in category_data]
        },
        'monthly_chart': {
            'labels': [item['month'] for item in monthly_data],
            'data': [item['total'] for item in monthly_data]
        },
        'status_chart': {
            'labels': [dict(AdditionalExpense.STATUS_CHOICES).get(item['status'], item['status']) for item in status_data],
            'data': [float(item['total']) for item in status_data],
            'counts': [item['count'] for item in status_data]
        }
    })

@login_required
def revenue_chart_data(request):
    # Données pour graphique en secteurs par catégorie
    category_data = AdditionalRevenue.objects.values(
        'category__name'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Données pour graphique temporel (6 derniers mois)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    monthly_data = []
    
    for i in range(6):
        month_start = six_months_ago + timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        monthly_total = AdditionalRevenue.objects.filter(
            date__gte=month_start,
            date__lt=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'total': float(monthly_total)
        })
    
    # Données par statut
    status_data = AdditionalRevenue.objects.values(
        'status'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    return JsonResponse({
        'category_chart': {
            'labels': [item['category__name'] for item in category_data],
            'data': [float(item['total']) for item in category_data],
            'counts': [item['count'] for item in category_data]
        },
        'monthly_chart': {
            'labels': [item['month'] for item in monthly_data],
            'data': [item['total'] for item in monthly_data]
        },
        'status_chart': {
            'labels': [dict(AdditionalRevenue.STATUS_CHOICES).get(item['status'], item['status']) for item in status_data],
            'data': [float(item['total']) for item in status_data],
            'counts': [item['count'] for item in status_data]
        }
    })