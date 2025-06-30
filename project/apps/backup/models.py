# apps/backup/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BackupJob(models.Model):
    JOB_TYPES = [
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    ]
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('xml', 'XML'),
        ('sql', 'SQL'),
    ]
    
    COMPRESSION_CHOICES = [
        ('none', 'Aucune'),
        ('zip', 'ZIP'),
        ('gzip', 'GZIP'),
    ]
    
    job_type = models.CharField(max_length=10, choices=JOB_TYPES, verbose_name="Type d'opération")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, verbose_name="Format")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Export options
    compression = models.CharField(max_length=10, choices=COMPRESSION_CHOICES, default='zip', verbose_name="Compression")
    include_media = models.BooleanField(default=False, verbose_name="Inclure les fichiers média")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Data selection
    include_customers = models.BooleanField(default=True, verbose_name="Inclure les clients")
    include_products = models.BooleanField(default=True, verbose_name="Inclure les produits")
    include_orders = models.BooleanField(default=True, verbose_name="Inclure les commandes")
    include_invoices = models.BooleanField(default=True, verbose_name="Inclure les factures")
    include_suppliers = models.BooleanField(default=True, verbose_name="Inclure les fournisseurs")
    include_company = models.BooleanField(default=True, verbose_name="Inclure les infos entreprise")
    include_audit = models.BooleanField(default=True, verbose_name="Inclure les données d'audit")
    
    # Date filters
    date_from = models.DateField(null=True, blank=True, verbose_name="Date de début")
    date_to = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    
    # Files
    export_file = models.FileField(upload_to='backups/exports/', blank=True, verbose_name="Fichier d'export")
    import_file = models.FileField(upload_to='backups/imports/', blank=True, verbose_name="Fichier d'import")
    
    # Job info
    total_records = models.IntegerField(default=0, verbose_name="Total d'enregistrements")
    processed_records = models.IntegerField(default=0, verbose_name="Enregistrements traités")
    error_count = models.IntegerField(default=0, verbose_name="Nombre d'erreurs")
    log_messages = models.TextField(blank=True, verbose_name="Messages de log")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Tâche de sauvegarde"
        verbose_name_plural = "Tâches de sauvegarde"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_job_type_display()} {self.get_format_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def add_log(self, message):
        """Add a log message"""
        if self.log_messages:
            self.log_messages += f"\n{message}"
        else:
            self.log_messages = message
        self.save()
    
    def get_progress_percentage(self):
        """Calculate progress percentage"""
        if self.total_records == 0:
            return 0
        return min(100, (self.processed_records / self.total_records) * 100)