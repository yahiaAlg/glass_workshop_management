from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import BackupRecord, RestoreRecord
from .resources import BackupRecordResource, RestoreRecordResource


@admin.register(BackupRecord)
class BackupRecordAdmin(ImportExportModelAdmin):
    resource_class = BackupRecordResource
    list_display = ('name', 'backup_type', 'status', 'file_size_mb', 'created_by', 'created_at', 'file_exists')
    list_filter = ('backup_type', 'status', 'created_at')
    search_fields = ('name', 'created_by__username', 'created_by__email')
    readonly_fields = ('created_at', 'file_size_mb', 'file_exists')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'backup_type', 'status')
        }),
        ('Fichier', {
            'fields': ('file_path', 'file_size', 'file_size_mb', 'file_exists')
        }),
        ('Utilisateur et dates', {
            'fields': ('created_by', 'created_at')
        }),
        ('Erreurs', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(RestoreRecord)
class RestoreRecordAdmin(ImportExportModelAdmin):
    resource_class = RestoreRecordResource
    list_display = ('file_name', 'backup_record', 'status', 'restored_by', 'restored_at')
    list_filter = ('status', 'restored_at')
    search_fields = ('file_name', 'restored_by__username', 'restored_by__email')
    readonly_fields = ('restored_at',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('file_name', 'backup_record', 'status')
        }),
        ('Utilisateur et dates', {
            'fields': ('restored_by', 'restored_at')
        }),
        ('Erreurs', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('restored_by', 'backup_record')