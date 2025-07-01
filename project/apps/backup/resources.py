# apps/backup/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth import get_user_model
from .models import BackupJob

User = get_user_model()

class BackupJobResource(resources.ModelResource):
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'username')
    )
    
    job_type_display = fields.Field(
        column_name='job_type_display',
        attribute='get_job_type_display'
    )
    
    status_display = fields.Field(
        column_name='status_display',
        attribute='get_status_display'
    )
    
    format_display = fields.Field(
        column_name='format_display',
        attribute='get_format_display'
    )
    
    compression_display = fields.Field(
        column_name='compression_display',
        attribute='get_compression_display'
    )
    
    progress = fields.Field(
        column_name='progress',
        attribute='get_progress_percentage'
    )

    class Meta:
        model = BackupJob
        fields = (
            'id', 'job_type', 'job_type_display', 'format', 'format_display',
            'status', 'status_display', 'compression', 'compression_display',
            'include_media', 'description', 
            'include_customers', 'include_products', 'include_orders',
            'include_invoices', 'include_suppliers', 'include_company',
            'include_audit', 'date_from', 'date_to',
            'total_records', 'processed_records', 'error_count',
            'created_by', 'created_at', 'completed_at', 'progress'
        )
        export_order = fields
        import_id_fields = ['id']
        skip_unchanged = True
        report_skipped = True
        exclude = ('log_messages', 'export_file', 'import_file')