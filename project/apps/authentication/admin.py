from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from import_export.admin import ImportExportModelAdmin
from .resources import UserResource

User = get_user_model()

@admin.register(User)
class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = UserResource
    
    # Import/Export settings
    import_template_name = 'admin/import_export/import.html'
    export_template_name = 'admin/import_export/export.html'
    
    # Display settings
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    
    # Fieldsets for editing
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'phone', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # Fieldsets for adding new users
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'phone', 'email', 'first_name', 'last_name')
        }),
    )
    
    # Import/Export customization
    def get_export_filename(self, request, queryset, file_format):
        """Customize export filename"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"users_export_{timestamp}.{file_format.get_extension()}"
    
    def get_import_data_kwargs(self, request, **kwargs):
        """Customize import data kwargs"""
        kwargs.update({
            'user': request.user,
        })
        return kwargs
    
    # Custom admin methods
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related()
    
    @admin.action(description="Activer les utilisateurs sélectionnés")
    def make_active(self, request, queryset):
        """Custom action to activate users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} utilisateur(s) activé(s).")
    
    @admin.action(description="Désactiver les utilisateurs sélectionnés")
    def make_inactive(self, request, queryset):
        """Custom action to deactivate users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} utilisateur(s) désactivé(s).")
    
    actions = ['make_active', 'make_inactive'] + list(BaseUserAdmin.actions or [])