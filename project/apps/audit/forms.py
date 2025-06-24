from django import forms
from .models import *

class AdditionalExpenseForm(forms.ModelForm):
    class Meta:
        model = AdditionalExpense
        fields = ['title', 'description', 'category', 'amount', 'date', 'status', 'vendor', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active categories
        self.fields['category'].queryset = ExpenseCategory.objects.filter(is_active=True)
        # Add empty option
        self.fields['category'].empty_label = "Sélectionner une catégorie"

class AdditionalRevenueForm(forms.ModelForm):
    class Meta:
        model = AdditionalRevenue
        fields = ['title', 'description', 'category', 'amount', 'date', 'status', 'client', 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'client': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active categories
        self.fields['category'].queryset = RevenueCategory.objects.filter(is_active=True)
        # Add empty option
        self.fields['category'].empty_label = "Sélectionner une catégorie"

class ExpenseDocumentForm(forms.ModelForm):
    class Meta:
        model = ExpenseDocument
        fields = ['file', 'name', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class RevenueDocumentForm(forms.ModelForm):
    class Meta:
        model = RevenueDocument
        fields = ['file', 'name', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }