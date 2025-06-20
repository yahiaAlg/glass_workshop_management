from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_type': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'fax': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'rc': forms.TextInput(attrs={'class': 'form-control'}),
            'art': forms.TextInput(attrs={'class': 'form-control'}),
            'nis': forms.TextInput(attrs={'class': 'form-control'}),
            'nif': forms.TextInput(attrs={'class': 'form-control'}),
            'rib': forms.TextInput(attrs={'class': 'form-control'}),
            'capital_social': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'operating_hours': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }