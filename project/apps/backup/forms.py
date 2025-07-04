from django import forms
from .models import BackupRecord

class BackupForm(forms.ModelForm):
    EXCLUDE_APPS = [
        'contenttypes',
        'auth.permission',
        'auth.group',
        'sessions',
        'admin.logentry',
    ]
    
    apps_to_backup = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Applications à sauvegarder"
    )
    
    exclude_sensitive = forms.BooleanField(
        required=False,
        initial=True,
        label="Exclure les données sensibles",
        help_text="Sessions, logs d'administration, etc."
    )
    
    class Meta:
        model = BackupRecord
        fields = ['name', 'backup_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la sauvegarde'}),
            'backup_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get available apps for backup
        from django.apps import apps
        app_choices = []
        for app in apps.get_app_configs():
            if app.name not in self.EXCLUDE_APPS and not app.name.startswith('django.'):
                app_choices.append((app.name, app.verbose_name or app.name))
        
        self.fields['apps_to_backup'].choices = app_choices

class RestoreForm(forms.Form):
    backup_file = forms.FileField(
        label="Fichier de sauvegarde",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.json'}),
        help_text="Sélectionnez un fichier JSON de sauvegarde"
    )
    
    confirm_restore = forms.BooleanField(
        required=True,
        label="Je confirme vouloir restaurer cette sauvegarde",
        help_text="⚠️ Cette opération remplacera les données existantes"
    )

class BackupSelectForm(forms.Form):
    backup_record = forms.ModelChoiceField(
        queryset=BackupRecord.objects.filter(status='completed'),
        empty_label="Sélectionnez une sauvegarde",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Sauvegarde à restaurer"
    )
    
    confirm_restore = forms.BooleanField(
        required=True,
        label="Je confirme vouloir restaurer cette sauvegarde",
        help_text="⚠️ Cette opération remplacera les données existantes"
    )