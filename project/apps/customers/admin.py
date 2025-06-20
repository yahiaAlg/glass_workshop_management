from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'phone', 'email', 'status', 'created_at')
    list_filter = ('customer_type', 'status', 'created_at')
    search_fields = ('name', 'phone', 'email', 'contact_person')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'customer_type', 'status')
        }),
        ('Contact', {
            'fields': ('address', 'phone', 'email', 'contact_person')
        }),
        ('Identifiants légaux', {
            'fields': ('nis', 'rc', 'art'),
            'classes': ('collapse',)
        }),
        ('Conditions commerciales', {
            'fields': ('payment_terms', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
    mark_as_active.short_description = "Marquer comme actif"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive')
    mark_as_inactive.short_description = "Marquer comme inactif"