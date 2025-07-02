from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Order, OrderItem
from .resources import OrderResource, OrderItemResource


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('subtotal', 'surface')
    fields = ('product', 'width', 'height', 'quantity', 'unit_price', 'subtotal', 'surface', 'notes')


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource
    list_display = (
        'order_number',
        'customer',
        'order_date',
        'delivery_date',
        'status',
        'total_amount',
        'installation_required'
    )
    list_filter = (
        'status',
        'installation_required',
        'order_date',
        'delivery_date'
    )
    search_fields = (
        'order_number',
        'customer__name',
        'customer__phone',
        'delivery_address'
    )
    readonly_fields = ('order_number', 'total_amount', 'created_at', 'updated_at')
    date_hierarchy = 'order_date'
    
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'order_number',
                'customer',
                'status',
                'total_amount'
            )
        }),
        ('Dates', {
            'fields': (
                'order_date',
                'delivery_date'
            )
        }),
        ('Livraison', {
            'fields': (
                'delivery_address',
                'installation_required'
            )
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [OrderItemInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('customer',)
        return self.readonly_fields


@admin.register(OrderItem)
class OrderItemAdmin(ImportExportModelAdmin):
    resource_class = OrderItemResource
    list_display = (
        'order',
        'product',
        'width',
        'height',
        'surface_display',
        'quantity',
        'unit_price',
        'subtotal'
    )
    list_filter = (
        'product',
        'order__status',
        'created_at'
    )
    search_fields = (
        'order__order_number',
        'product__name',
        'notes'
    )
    readonly_fields = ('subtotal', 'surface_display')
    
    def surface_display(self, obj):
        return f"{obj.surface:.2f} m²"
    surface_display.short_description = "Surface"
    
    fieldsets = (
        ('Commande', {
            'fields': ('order', 'product')
        }),
        ('Dimensions', {
            'fields': (
                ('width', 'height'),
                'surface_display',
                'quantity'
            )
        }),
        ('Prix', {
            'fields': (
                'unit_price',
                'subtotal'
            )
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )