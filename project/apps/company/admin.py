from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Company
from .resources import CompanyResource

@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    resource_class = CompanyResource
    list_display = ('name', 'business_type', 'phone', 'email', 'tax_rate', 'created_at')
    search_fields = ('name', 'business_type', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'business_type', 'logo')
        }),
        ('Contact', {
            'fields': ('address', 'phone', 'fax', 'email', 'website')
        }),
        ('Identifiants légaux', {
            'fields': ('rc', 'art', 'nis', 'nif', 'rib', 'capital_social'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('tax_rate', 'operating_hours', 'certifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )