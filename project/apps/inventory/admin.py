from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import GlassProduct
from .resources import GlassProductResource

@admin.register(GlassProduct)
class GlassProductAdmin(ImportExportModelAdmin):
    resource_class = GlassProductResource
    list_display = ('code', 'name', 'glass_type', 'thickness', 'color', 'selling_price', 'stock_quantity', 'is_low_stock', 'status')
    list_filter = ('glass_type', 'thickness', 'color', 'finish', 'status', 'supplier')
    search_fields = ('code', 'name', 'description')
    ordering = ('name',)
    readonly_fields = ('code', 'created_at', 'updated_at', 'profit_margin')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'name', 'description', 'image', 'status')
        }),
        ('Spécifications techniques', {
            'fields': ('glass_type', 'thickness', 'color', 'finish', 'unit')
        }),
        ('Prix et stock', {
            'fields': ('cost_price', 'selling_price', 'profit_margin', 'stock_quantity', 'minimum_stock')
        }),
        ('Fournisseur et catégorie', {
            'fields': ('supplier', 'category')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_active', 'mark_as_inactive', 'check_low_stock']
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
    mark_as_active.short_description = "Marquer comme actif"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive')
    mark_as_inactive.short_description = "Marquer comme inactif"
    
    def check_low_stock(self, request, queryset):
        low_stock_products = [p for p in queryset if p.is_low_stock()]
        if low_stock_products:
            self.message_user(request, f"{len(low_stock_products)} produits en stock faible")
        else:
            self.message_user(request, "Aucun produit en stock faible")
    check_low_stock.short_description = "Vérifier stock faible"
    
    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = "Stock faible"
    
    def profit_margin(self, obj):
        return f"{obj.profit_margin():.1f}%"
    profit_margin.short_description = "Marge bénéficiaire"