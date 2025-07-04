from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import GlassProduct, GlassType, GlassThickness, GlassColor, GlassFinish, Unit
from .resources import (
    GlassProductResource, GlassTypeResource, GlassThicknessResource, 
    GlassColorResource, GlassFinishResource, UnitResource
)

@admin.register(GlassType)
class GlassTypeAdmin(ImportExportModelAdmin):
    resource_class = GlassTypeResource
    list_display = ('code', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    list_editable = ('is_active',)

@admin.register(GlassThickness)
class GlassThicknessAdmin(ImportExportModelAdmin):
    resource_class = GlassThicknessResource
    list_display = ('value', 'display_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('value', 'display_name')
    list_editable = ('is_active',)

@admin.register(GlassColor)
class GlassColorAdmin(ImportExportModelAdmin):
    resource_class = GlassColorResource
    list_display = ('code', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    list_editable = ('is_active',)

@admin.register(GlassFinish)
class GlassFinishAdmin(ImportExportModelAdmin):
    resource_class = GlassFinishResource
    list_display = ('code', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    list_editable = ('is_active',)

@admin.register(Unit)
class UnitAdmin(ImportExportModelAdmin):
    resource_class = UnitResource
    list_display = ('code', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    list_editable = ('is_active',)

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
    
    # Add custom queryset method to only show active choices
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'glass_type':
            kwargs['queryset'] = GlassType.objects.filter(is_active=True)
        elif db_field.name == 'thickness':
            kwargs['queryset'] = GlassThickness.objects.filter(is_active=True)
        elif db_field.name == 'color':
            kwargs['queryset'] = GlassColor.objects.filter(is_active=True)
        elif db_field.name == 'finish':
            kwargs['queryset'] = GlassFinish.objects.filter(is_active=True)
        elif db_field.name == 'unit':
            kwargs['queryset'] = Unit.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
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