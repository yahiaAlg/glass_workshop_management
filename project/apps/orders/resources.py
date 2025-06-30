# apps/orders/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget

# Assuming Order model structure based on Invoice foreign key
class OrderResource(resources.ModelResource):
    customer = fields.Field(
        column_name='customer',
        attribute='customer',
        widget=ForeignKeyWidget('customers.Customer', 'name')
    )
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget('authentication.User', 'username')
    )
    order_date = fields.Field(
        attribute='order_date',
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
        # model = Order  # Uncomment when Order model is available
        fields = (
            'id', 'order_number', 'customer', 'order_date', 'delivery_date',
            'status', 'total_amount', 'notes', 'created_by', 'created_at', 'updated_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'

class OrderItemResource(resources.ModelResource):
    order = fields.Field(
        column_name='order',
        attribute='order',
        widget=ForeignKeyWidget('orders.Order', 'order_number')
    )
    product = fields.Field(
        column_name='product',
        attribute='product',
        widget=ForeignKeyWidget('inventory.GlassProduct', 'name')
    )
    created_at = fields.Field(
        attribute='created_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    class Meta:
        # model = OrderItem  # Uncomment when OrderItem model is available
        fields = (
            'id', 'order', 'product', 'description', 'quantity',
            'unit_price', 'subtotal', 'width', 'height', 'thickness',
            'created_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'