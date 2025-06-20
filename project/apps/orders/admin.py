from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'quantity', 'unit_price', 'subtotal', 'notes')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'order_date', 'delivery_date', 'status', 'total_amount', 'installation_required')
    list_filter = ('status', 'installation_required', 'order_date', 'delivery_date')
    search_fields = ('order_number', 'customer__name')
    ordering = ('-created_at',)
    readonly_fields = ('order_number', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('order_number', 'customer', 'status')
        }),
        ('Livraison', {
            'fields': ('delivery_date', 'delivery_address', 'installation_required')
        }),
        ('Détails', {
            'fields': ('total_amount', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_confirmed', 'mark_as_delivered']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Marquer comme confirmée"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Marquer comme livrée"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('order__status', 'product__glass_type')
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('subtotal',)