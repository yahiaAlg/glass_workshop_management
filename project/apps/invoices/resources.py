# apps/invoices/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget
from .models import Invoice, InvoiceItem, InvoiceService, Payment
from apps.authentication.models import User

class InvoiceResource(resources.ModelResource):
    customer = fields.Field(
        column_name='customer',
        attribute='customer',
        widget=ForeignKeyWidget('customers.Customer', field='name')
    )
    order = fields.Field(
        column_name='order',
        attribute='order',
        widget=ForeignKeyWidget('orders.Order', field='order_number'),
        saves_null_values=False  # Skip if order not found
    )
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget(User, field='username'),
        saves_null_values=False  # Skip if user not found
        
    )
    invoice_date = fields.Field(
        attribute='invoice_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    due_date = fields.Field(
        attribute='due_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    delivery_date = fields.Field(
        attribute='delivery_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    created_at = fields.Field(
        attribute='created_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    updated_at = fields.Field(
        attribute='updated_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    class Meta:
        model = Invoice
        fields = (
            'id', 'invoice_number', 'customer', 'order', 'invoice_date',
            'due_date', 'payment_method', 'delivery_address', 'delivery_date',
            'installation_notes', 'warranty_info', 'subtotal', 'services_total',
            'discount_amount', 'tax_amount', 'total_amount', 'status',
            'notes', 'created_by', 'created_at', 'updated_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'
        skip_unchanged = True
        report_skipped = False

class InvoiceItemResource(resources.ModelResource):
    invoice = fields.Field(
        column_name='invoice',
        attribute='invoice',
        widget=ForeignKeyWidget('invoices.Invoice', field='invoice_number')
    )
    product = fields.Field(
        column_name='product',
        attribute='product',
        widget=ForeignKeyWidget('inventory.GlassProduct', field='name')
    )
    created_at = fields.Field(
        attribute='created_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    class Meta:
        model = InvoiceItem
        fields = (
            'id', 'invoice', 'product', 'description', 'quantity',
            'unit_price', 'subtotal', 'width', 'height', 'thickness',
            'created_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'
        skip_unchanged = True
        report_skipped = False

class InvoiceServiceResource(resources.ModelResource):
    invoice = fields.Field(
        column_name='invoice',
        attribute='invoice',
        widget=ForeignKeyWidget('invoices.Invoice', field='invoice_number')
    )
    created_at = fields.Field(
        attribute='created_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    class Meta:
        model = InvoiceService
        fields = (
            'id', 'invoice', 'service_type', 'description', 'amount',
            'created_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'
        skip_unchanged = True
        report_skipped = False

class PaymentResource(resources.ModelResource):
    invoice = fields.Field(
        column_name='invoice',
        attribute='invoice',
        widget=ForeignKeyWidget('invoices.Invoice', field='invoice_number')
    )
    payment_date = fields.Field(
        attribute='payment_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    created_at = fields.Field(
        attribute='created_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    class Meta:
        model = Payment
        fields = (
            'id', 'invoice', 'payment_date', 'amount', 'payment_method',
            'reference', 'status', 'notes', 'created_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'
        skip_unchanged = True
        report_skipped = False