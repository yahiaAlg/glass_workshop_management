from import_export import resources, fields
from import_export.widgets import DateTimeWidget, BooleanWidget
from django.contrib.auth import get_user_model

User = get_user_model()

class UserResource(resources.ModelResource):
    # Custom field for role display
    role_display = fields.Field(
        column_name='role_display',
        attribute='get_role_display',
        readonly=True
    )
    
    # Custom formatting for dates
    created_at = fields.Field(
        attribute='created_at',
        column_name='created_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    updated_at = fields.Field(
        attribute='updated_at',
        column_name='updated_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    # Boolean fields with custom widget
    is_active = fields.Field(
        attribute='is_active',
        column_name='is_active',
        widget=BooleanWidget()
    )
    
    is_staff = fields.Field(
        attribute='is_staff',
        column_name='is_staff',
        widget=BooleanWidget()
    )
    
    is_superuser = fields.Field(
        attribute='is_superuser',
        column_name='is_superuser',
        widget=BooleanWidget()
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'role_display', 'phone', 'is_active', 'is_staff', 
            'is_superuser', 'date_joined', 'last_login', 'created_at', 'updated_at'
        )
        export_order = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'role_display', 'phone', 'is_active', 'is_staff', 
            'is_superuser', 'created_at', 'updated_at', 'date_joined', 'last_login'
        )
        import_id_fields = ('username',)
        skip_unchanged = True
        report_skipped = True
    
    def before_import_row(self, row, **kwargs):
        """Clean and validate data before import"""
        # Clean email
        if 'email' in row:
            row['email'] = row['email'].strip().lower() if row['email'] else ''
        
        # Clean username
        if 'username' in row:
            row['username'] = row['username'].strip() if row['username'] else ''
            
        # Validate role
        if 'role' in row and row['role']:
            valid_roles = ['admin', 'worker']
            if row['role'] not in valid_roles:
                row['role'] = 'worker'  # Default to worker if invalid
    
    def after_save_instance(self, instance, using_transactions, dry_run):
        """Actions after saving instance"""
        if not dry_run:
            # Set password if it's a new user and no password is set
            if not instance.password:
                instance.set_password('changeme123')  # Default password
                instance.save()
    
    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Skip rows based on custom logic"""
        # Skip if username is empty
        if not row.get('username', '').strip():
            return True
        return super().skip_row(instance, original, row, import_validation_errors)
    
    def get_export_queryset(self, queryset):
        """Customize export queryset"""
        return queryset.select_related().order_by('-created_at')