# apps/backup/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from .models import BackupJob
from .resources import BackupJobResource

@admin.register(BackupJob)
class BackupJobAdmin(ImportExportModelAdmin):
    resource_class = BackupJobResource
    
    list_display = ('job_type_display', 'format_display', 'status_display', 
                    'created_by', 'created_at', 'progress_bar')
    list_filter = ('job_type', 'format', 'status', 'created_by', 'created_at')
    search_fields = ('description', 'log_messages', 'created_by__username')
    readonly_fields = ('created_at', 'completed_at', 'total_records', 
                       'processed_records', 'error_count', 'progress_bar')
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('job_type', 'format', 'status', 'description', 'created_by')
        }),
        (_('Options d\'export'), {
            'fields': ('compression', 'include_media'),
            'classes': ('collapse',),
        }),
        (_('Sélection des données'), {
            'fields': ('include_customers', 'include_products', 'include_orders', 
                       'include_invoices', 'include_suppliers', 'include_company', 'include_audit'),
            'classes': ('collapse',),
        }),
        (_('Filtres de date'), {
            'fields': ('date_from', 'date_to'),
            'classes': ('collapse',),
        }),
        (_('Fichiers'), {
            'fields': ('export_file', 'import_file'),
        }),
        (_('Progression et résultats'), {
            'fields': ('total_records', 'processed_records', 'error_count', 'progress_bar', 'log_messages'),
        }),
        (_('Dates'), {
            'fields': ('created_at', 'completed_at'),
        }),
    )
    
    def job_type_display(self, obj):
        return obj.get_job_type_display()
    job_type_display.short_description = _("Type d'opération")
    
    def format_display(self, obj):
        return obj.get_format_display()
    format_display.short_description = _("Format")
    
    def status_display(self, obj):
        status_colors = {
            'pending': '#FFC107',    # Yellow
            'processing': '#2196F3', # Blue
            'completed': '#4CAF50',  # Green
            'failed': '#F44336',     # Red
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            status_colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = _("Statut")
    
    def progress_bar(self, obj):
        percentage = obj.get_progress_percentage()
        color = '#4CAF50'  # Green
        
        if obj.status == 'failed':
            color = '#F44336'  # Red
        
        return format_html(
            '''
            <div style="width:100%; background-color:#f0f0f0; height:20px; border-radius:3px;">
                <div style="width:{}%; background-color:{}; height:20px; border-radius:3px; text-align:center; color:white;">
                    {}%
                </div>
            </div>
            ''',
            percentage,
            color,
            int(percentage)
        )
    progress_bar.short_description = _("Progression")
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)