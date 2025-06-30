from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Supplier
from .resources import SupplierResource

@admin.register(Supplier)
class SupplierAdmin(ImportExportModelAdmin):
    resource_class = SupplierResource
    list_display = ('name', 'contact_person', 'phone', 'email', 'status', 'last_order_date')
    list_filter = ('status', 'last_order_date', 'created_at')
    search_fields = ('name', 'contact_person', 'phone', 'email')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'contact_person', 'status')
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Conditions commerciales', {
            'fields': ('payment_terms', 'last_order_date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )