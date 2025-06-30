from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Invoice, InvoiceItem, InvoiceService, Payment
from .resources import InvoiceResource, InvoiceItemResource, InvoiceServiceResource, PaymentResource

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'description', 'quantity', 'unit_price', 'subtotal', 'width', 'height', 'thickness')

class InvoiceServiceInline(admin.TabularInline):
    model = InvoiceService
    extra = 0
    fields = ('service_type', 'description', 'amount')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('payment_date', 'amount', 'payment_method', 'reference', 'status', 'notes')

@admin.register(Invoice)
class InvoiceAdmin(ImportExportModelAdmin):
    resource_class = InvoiceResource
    list_display = ('invoice_number', 'customer', 'invoice_date', 'due_date', 'status', 'total_amount', 'payment_method')
    list_filter = ('status', 'payment_method', 'invoice_date', 'due_date')
    search_fields = ('invoice_number', 'customer__name')
    ordering = ('-created_at',)
    readonly_fields = ('invoice_number', 'subtotal', 'services_total', 'tax_amount', 'total_amount', 'created_at', 'updated_at')
    inlines = [InvoiceItemInline, InvoiceServiceInline, PaymentInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('invoice_number', 'customer', 'order', 'status', 'created_by')
        }),
        ('Dates', {
            'fields': ( 'due_date', 'delivery_date')
        }),
        ('Livraison et installation', {
            'fields': ('delivery_address', 'installation_notes', 'warranty_info')
        }),
        ('Totaux', {
            'fields': ('subtotal', 'services_total', 'discount_amount', 'tax_amount', 'total_amount')
        }),
        ('Paiement', {
            'fields': ('payment_method', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_sent', 'mark_as_paid', 'recalculate_totals']
    
    def mark_as_sent(self, request, queryset):
        queryset.update(status='sent')
    mark_as_sent.short_description = "Marquer comme envoyée"
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
    mark_as_paid.short_description = "Marquer comme payée"
    
    def recalculate_totals(self, request, queryset):
        for invoice in queryset:
            invoice.calculate_totals()
        self.message_user(request, f"Totaux recalculés pour {queryset.count()} factures")
    recalculate_totals.short_description = "Recalculer les totaux"

@admin.register(InvoiceItem)
class InvoiceItemAdmin(ImportExportModelAdmin):
    resource_class = InvoiceItemResource
    list_display = ('invoice', 'product', 'quantity', 'unit_price', 'subtotal', 'width', 'height')
    list_filter = ('product__glass_type', 'thickness')
    search_fields = ('invoice__invoice_number', 'product__name', 'description')
    readonly_fields = ('subtotal',)

@admin.register(InvoiceService)
class InvoiceServiceAdmin(ImportExportModelAdmin):
    resource_class = InvoiceServiceResource
    list_display = ('invoice', 'service_type', 'description', 'amount')
    list_filter = ('service_type',)
    search_fields = ('invoice__invoice_number', 'description')

@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    resource_class = PaymentResource
    list_display = ('invoice', 'payment_date', 'amount', 'payment_method', 'status', 'reference')
    list_filter = ('payment_method', 'status', 'payment_date')
    search_fields = ('invoice__invoice_number', 'reference')
    ordering = ('-payment_date',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('invoice', 'payment_date', 'amount', 'status')
        }),
        ('Détails de paiement', {
            'fields': ('payment_method', 'reference', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )