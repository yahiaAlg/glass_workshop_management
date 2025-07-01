# apps/orders/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget
from .models import Order, OrderItem
from apps.customers.models import Customer
from apps.inventory.models import GlassProduct

            
            
class OrderResource(resources.ModelResource):
    customer = fields.Field(
        column_name='customer',
        attribute='customer',
        widget=ForeignKeyWidget(Customer, 'name')
    )
    order_date = fields.Field(
        column_name='order_date',
        attribute='order_date',
        widget=DateWidget('%Y-%m-%d %H:%M:%S')
    )
    delivery_date = fields.Field(
        column_name='delivery_date',
        attribute='delivery_date',
        widget=DateWidget('%Y-%m-%d')
    )
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'customer', 'order_date', 'delivery_date',
            'status', 'delivery_address', 'installation_required', 'notes',
            'total_amount'
        )
        export_order = fields
        import_id_fields = ('order_number',)
    
    def before_import_row(self, row, **kwargs):
        # Auto-generate order number if not provided
        if not row.get('order_number'):
            row['order_number'] = ''
    
    def after_save_instance(self, instance, row, **kwargs):
        if not kwargs.get('dry_run', False):
            instance.calculate_total()


class OrderItemResource(resources.ModelResource):
    order = fields.Field(
        column_name='order',
        attribute='order',
        widget=ForeignKeyWidget(Order, 'order_number')
    )
    product = fields.Field(
        column_name='product',
        attribute='product',
        widget=ForeignKeyWidget(GlassProduct, 'name')
    )
    surface = fields.Field(
        column_name='surface_m2',
        attribute='surface',
        readonly=True
    )
    
    class Meta:
        model = OrderItem
        fields = (
            'id', 'order', 'product', 'width', 'height', 'quantity',
            'unit_price', 'subtotal', 'surface', 'notes'
        )
        export_order = fields
        import_id_fields = ('id',)
    
    def dehydrate_surface(self, orderitem):
        return float(orderitem.surface)
    
    def after_save_instance(self, instance, row, **kwargs):
        if not kwargs.get('dry_run', False):
            instance.order.calculate_total()