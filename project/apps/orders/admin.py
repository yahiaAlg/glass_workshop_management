from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Order, OrderItem
from .resources import OrderResource, OrderItemResource

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'width', 'height', 'quantity', 'unit_price', 'subtotal', 'notes')
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource
    list_display = (
        'order_number', 'customer', 'order_date', 'delivery_date',
        'status', 'total_amount', 'installation_required'
    )
    list_filter = ('status', 'installation_required', 'order_date', 'delivery_date')
    search_fields = ('order_number', 'customer__name', 'customer__email')
    readonly_fields = ('order_number', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('order_number', 'customer', 'status')
        }),
        ('Dates', {
            'fields': ('order_date', 'delivery_date')
        }),
        ('Livraison', {
            'fields': ('delivery_address', 'installation_required')
        }),
        ('Détails financiers', {
            'fields': ('total_amount',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_total()


@admin.register(OrderItem)
class OrderItemAdmin(ImportExportModelAdmin):
    resource_class = OrderItemResource
    list_display = (
        'order', 'product', 'width', 'height', 'quantity',
        'unit_price', 'subtotal', 'surface_display'
    )
    list_filter = ('product', 'order__status')
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('subtotal', 'surface_display')
    
    fieldsets = (
        ('Commande', {
            'fields': ('order', 'product')
        }),
        ('Dimensions', {
            'fields': ('width', 'height', 'surface_display')
        }),
        ('Prix', {
            'fields': ('quantity', 'unit_price', 'subtotal')
        }),
        ('Notes', {
            'fields': ('notes',)
        })
    )
    
    def surface_display(self, obj):
        return f"{obj.surface:.4f} m²"
    surface_display.short_description = "Surface"
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.order.calculate_total()