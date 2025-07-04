from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from django.contrib.auth import get_user_model
from .models import BackupRecord, RestoreRecord

User = get_user_model()


class BackupRecordResource(resources.ModelResource):
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'username')
    )
    created_at = fields.Field(
        column_name='created_at',
        attribute='created_at',
        widget=DateTimeWidget()
    )
    file_size_mb = fields.Field(
        column_name='file_size_mb',
        attribute='file_size_mb',
        readonly=True
    )
    file_exists = fields.Field(
        column_name='file_exists',
        attribute='file_exists',
        readonly=True
    )
    backup_type_display = fields.Field(
        column_name='backup_type_display',
        attribute='get_backup_type_display',
        readonly=True
    )
    status_display = fields.Field(
        column_name='status_display',
        attribute='get_status_display',
        readonly=True
    )
    
    class Meta:
        model = BackupRecord
        fields = (
            'id',
            'name',
            'backup_type',
            'backup_type_display',
            'file_path',
            'file_size',
            'file_size_mb',
            'created_by',
            'created_at',
            'status',
            'status_display',
            'error_message',
            'file_exists'
        )
        export_order = (
            'id',
            'name',
            'backup_type',
            'backup_type_display',
            'status',
            'status_display',
            'file_path',
            'file_size',
            'file_size_mb',
            'file_exists',
            'created_by',
            'created_at',
            'error_message'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
    
    def dehydrate_created_by(self, backup_record):
        return backup_record.created_by.username if backup_record.created_by else ''
    
    def before_import_row(self, row, **kwargs):
        """Clean and validate data before import"""
        # Ensure required fields are present
        if not row.get('name'):
            raise ValueError("Le nom de la sauvegarde est requis")
        
        # Validate backup_type
        valid_types = ['full', 'partial']
        if row.get('backup_type') not in valid_types:
            row['backup_type'] = 'full'
        
        # Validate status
        valid_statuses = ['pending', 'processing', 'completed', 'failed']
        if row.get('status') not in valid_statuses:
            row['status'] = 'pending'


class RestoreRecordResource(resources.ModelResource):
    backup_record = fields.Field(
        column_name='backup_record',
        attribute='backup_record',
        widget=ForeignKeyWidget(BackupRecord, 'name')
    )
    restored_by = fields.Field(
        column_name='restored_by',
        attribute='restored_by',
        widget=ForeignKeyWidget(User, 'username')
    )
    restored_at = fields.Field(
        column_name='restored_at',
        attribute='restored_at',
        widget=DateTimeWidget()
    )
    status_display = fields.Field(
        column_name='status_display',
        attribute='get_status_display',
        readonly=True
    )
    backup_record_name = fields.Field(
        column_name='backup_record_name',
        attribute='backup_record__name',
        readonly=True
    )
    
    class Meta:
        model = RestoreRecord
        fields = (
            'id',
            'backup_record',
            'backup_record_name',
            'file_name',
            'restored_by',
            'restored_at',
            'status',
            'status_display',
            'error_message'
        )
        export_order = (
            'id',
            'file_name',
            'backup_record',
            'backup_record_name',
            'status',
            'status_display',
            'restored_by',
            'restored_at',
            'error_message'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
    
    def dehydrate_restored_by(self, restore_record):
        return restore_record.restored_by.username if restore_record.restored_by else ''
    
    def dehydrate_backup_record(self, restore_record):
        return restore_record.backup_record.name if restore_record.backup_record else ''
    
    def before_import_row(self, row, **kwargs):
        """Clean and validate data before import"""
        # Ensure required fields are present
        if not row.get('file_name'):
            raise ValueError("Le nom du fichier est requis")
        
        # Validate status
        valid_statuses = ['pending', 'processing', 'completed', 'failed']
        if row.get('status') not in valid_statuses:
            row['status'] = 'pending'