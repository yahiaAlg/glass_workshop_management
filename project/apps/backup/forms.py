# apps/backup/forms.py
from django import forms
from .models import BackupJob

class ExportForm(forms.ModelForm):
    # Add missing fields that the template expects
    COMPRESSION_CHOICES = [
        ('none', 'Aucune'),
        ('zip', 'ZIP'),
        ('gzip', 'GZIP'),
    ]
    
    compression = forms.ChoiceField(
        choices=COMPRESSION_CHOICES,
        initial='zip',
        label="Compression",
        help_text="Type de compression pour le fichier d'export",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Tables selection as individual checkboxes
    tables = forms.MultipleChoiceField(
        choices=[
            ('customers', 'Clients'),
            ('products', 'Produits'),
            ('orders', 'Commandes'),
            ('invoices', 'Factures'),
            ('suppliers', 'Fournisseurs'),
            ('company', 'Informations entreprise'),
            ('audit', 'Données d\'audit'),
        ],
        widget=forms.CheckboxSelectMultiple,
        label="Tables à exporter",
        help_text="Sélectionnez les données à inclure dans l'export",
        required=False
    )
    
    include_media = forms.BooleanField(
        required=False,
        initial=False,
        label="Inclure les fichiers média",
        help_text="Inclure les images et documents (augmente la taille du fichier)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    description = forms.CharField(
        required=False,
        max_length=500,
        label="Description",
        help_text="Description optionnelle de cet export",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Description de cet export...'
        })
    )

    class Meta:
        model = BackupJob
        fields = [
            'format',
            'date_from',
            'date_to'
        ]
        widgets = {
            'format': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_format'
            }),
            'date_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_date_from'
            }),
            'date_to': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_date_to'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial values for tables based on model boolean fields
        initial_tables = []
        if self.instance and self.instance.pk:
            if self.instance.include_customers:
                initial_tables.append('customers')
            if self.instance.include_products:
                initial_tables.append('products')
            if self.instance.include_orders:
                initial_tables.append('orders')
            if self.instance.include_invoices:
                initial_tables.append('invoices')
            if self.instance.include_suppliers:
                initial_tables.append('suppliers')
            if self.instance.include_company:
                initial_tables.append('company')
            if hasattr(self.instance, 'include_audit') and self.instance.include_audit:
                initial_tables.append('audit')
        else:
            # Default to all tables selected
            initial_tables = ['customers', 'products', 'orders', 'invoices', 'suppliers', 'company', 'audit']
            
        self.fields['tables'].initial = initial_tables
        
        # Add labels
        self.fields['format'].label = "Format d'export"
        self.fields['date_from'].label = "Date de début"
        self.fields['date_to'].label = "Date de fin"
        
        # Add help text
        self.fields['format'].help_text = "Format du fichier d'export"
        self.fields['date_from'].help_text = "Exporter les données à partir de cette date"
        self.fields['date_to'].help_text = "Exporter les données jusqu'à cette date"
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convert tables selection to individual boolean fields
        selected_tables = self.cleaned_data.get('tables', [])
        instance.include_customers = 'customers' in selected_tables
        instance.include_products = 'products' in selected_tables
        instance.include_orders = 'orders' in selected_tables
        instance.include_invoices = 'invoices' in selected_tables
        instance.include_suppliers = 'suppliers' in selected_tables
        instance.include_company = 'company' in selected_tables
        
        if hasattr(instance, 'include_audit'):
            instance.include_audit = 'audit' in selected_tables
        
        if commit:
            instance.save()
        return instance

class ImportForm(forms.ModelForm):
    class Meta:
        model = BackupJob
        fields = ['format', 'import_file']
        widgets = {
            'format': forms.Select(attrs={'class': 'form-select'}),
            'import_file': forms.FileInput(attrs={'class': 'form-control'}),
        }