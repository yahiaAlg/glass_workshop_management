# apps/backup/forms.py
from django import forms
from .models import BackupJob

class ExportForm(forms.Form):
    format = forms.ChoiceField(
        choices=BackupJob.FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Format d'export"
    )
    
    # Data selection
    include_customers = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Clients"
    )
    
    include_products = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Produits"
    )
    
    include_orders = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Commandes"
    )
    
    include_invoices = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Factures"
    )
    
    include_suppliers = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Fournisseurs"
    )
    
    include_company = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Informations entreprise"
    )
    
    # Date filters
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date de début"
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date de fin"
    )

class ImportForm(forms.Form):
    format = forms.ChoiceField(
        choices=BackupJob.FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Format du fichier"
    )
    
    import_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.json,.xlsx,.csv,.zip'
        }),
        label="Fichier à importer"
    )
    
    def clean_import_file(self):
        file = self.cleaned_data.get('import_file')
        format_type = self.cleaned_data.get('format')
        
        if file:
            # Check file extension based on format
            filename = file.name.lower()
            
            if format_type == 'json' and not filename.endswith('.json'):
                raise forms.ValidationError("Le fichier doit être au format JSON (.json)")
            elif format_type == 'excel' and not filename.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError("Le fichier doit être au format Excel (.xlsx, .xls)")
            elif format_type == 'csv' and not filename.endswith(('.csv', '.zip')):
                raise forms.ValidationError("Le fichier doit être au format CSV (.csv) ou ZIP (.zip)")
            
            # Check file size (max 50MB)
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError("Le fichier ne peut pas dépasser 50MB")
        
        return file