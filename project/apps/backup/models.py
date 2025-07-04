from django.db import models
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class BackupRecord(models.Model):
    BACKUP_TYPE_CHOICES = [
        ('full', 'Sauvegarde Complète'),
        ('partial', 'Sauvegarde Partielle'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminée'),
        ('failed', 'Échouée'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom de la sauvegarde")
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPE_CHOICES, default='full')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="Taille (bytes)")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Enregistrement de Sauvegarde"
        verbose_name_plural = "Enregistrements de Sauvegarde"
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    @property
    def file_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def file_exists(self):
        if self.file_path:
            return os.path.exists(self.file_path)
        return False

class RestoreRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminée'),
        ('failed', 'Échouée'),
    ]
    
    backup_record = models.ForeignKey(BackupRecord, on_delete=models.CASCADE, null=True, blank=True)
    file_name = models.CharField(max_length=200)
    restored_by = models.ForeignKey(User, on_delete=models.CASCADE)
    restored_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-restored_at']
        verbose_name = "Enregistrement de Restauration"
        verbose_name_plural = "Enregistrements de Restauration"
    
    def __str__(self):
        return f"Restauration {self.file_name} - {self.get_status_display()}"