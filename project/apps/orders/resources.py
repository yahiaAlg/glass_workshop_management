from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DecimalWidget
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem
from apps.customers.models import Customer
from apps.inventory.models import GlassProduct
import decimal

class CustomDecimalWidget(DecimalWidget):
    """Widget to handle decimal with period as decimal separator"""
    def clean(self, value, row=None, *args, **kwargs):
        if value is None or value == '':
            return None
        try:
            # Handle both period and comma as decimal separators
            if isinstance(value, str):
                value = value.replace(',', '.')
            return decimal.Decimal(str(value))
        except (ValueError, decimal.InvalidOperation):
            return None
    
    def render(self, value, obj=None, **kwargs):
        # Accept any additional kwargs passed by django-import-export
        if value is None:
            return ""
        # Use period as decimal separator for export
        return str(value).replace(',', '.')

class OrderResource(resources.ModelResource):
    customer = fields.Field(
        column_name='client',
        attribute='customer',
        widget=ForeignKeyWidget(Customer, 'name')
    )
    
    status_display = fields.Field(
        column_name='statut',
        attribute='status'
    )
    
    total_amount = fields.Field(
        column_name='total_amount',
        attribute='total_amount',
        widget=CustomDecimalWidget()
    )
    
    class Meta:
        model = Order
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ['order_number']
        fields = [
            'id', 'order_number', 'customer', 'order_date', 'delivery_date', 
            'status', 'status_display', 'delivery_address', 'installation_required', 
            'notes', 'total_amount'
        ]
        export_order = fields
        verbose_name = _("Commande")
        
    def dehydrate_status_display(self, order):
        return dict(Order.STATUS_CHOICES).get(order.status, order.status)


class OrderItemResource(resources.ModelResource):
    order = fields.Field(
        column_name='commande',
        attribute='order',
        widget=ForeignKeyWidget(Order, 'order_number')
    )
    
    product = fields.Field(
        column_name='produit',
        attribute='product',
        widget=ForeignKeyWidget(GlassProduct, 'name')
    )
    
    surface_area = fields.Field(
        column_name='surface_m2',
        attribute='surface',
        widget=CustomDecimalWidget()
    )
    
    # Define decimal fields with custom widget
    width = fields.Field(
        column_name='width',
        attribute='width',
        widget=CustomDecimalWidget()
    )
    
    height = fields.Field(
        column_name='height',
        attribute='height',
        widget=CustomDecimalWidget()
    )
    
    quantity = fields.Field(
        column_name='quantity',
        attribute='quantity',
        widget=CustomDecimalWidget()
    )
    
    unit_price = fields.Field(
        column_name='unit_price',
        attribute='unit_price',
        widget=CustomDecimalWidget()
    )
    
    subtotal = fields.Field(
        column_name='subtotal',
        attribute='subtotal',
        widget=CustomDecimalWidget()
    )
    
    class Meta:
        model = OrderItem
        skip_unchanged = True
        report_skipped = False  # Changed to False to get more detailed errors
        use_transactions = True  # Add transaction support
        fields = [
            'id', 'order', 'product', 'width', 'height', 
            'quantity', 'unit_price', 'subtotal', 'notes', 'surface_area'
        ]
        export_order = fields
        verbose_name = _("Article de commande")
    
    def before_import_row(self, row, **kwargs):
        """Prepare data before import"""
        try:
            # Make sure all required fields are present
            order_number = row.get('commande')
            product_name = row.get('produit')
            
            if not order_number or not product_name:
                return
                
            # Convert decimal values safely
            width = self._safe_decimal(row.get('width'))
            height = self._safe_decimal(row.get('height'))
            quantity = self._safe_decimal(row.get('quantity'))
            unit_price = self._safe_decimal(row.get('unit_price'))
            
            if width is None or height is None or quantity is None or unit_price is None:
                return
                
            # Calculate surface and subtotal
            surface = (width * height) / 10000  # Convert cm² to m²
            subtotal = surface * quantity * unit_price
            
            # Update the row with processed values
            row['width'] = str(width)
            row['height'] = str(height)
            row['quantity'] = str(quantity)
            row['unit_price'] = str(unit_price)
            row['subtotal'] = str(subtotal)
            row['surface_m2'] = str(surface)
            
        except Exception as e:
            # Log error but don't crash
            print(f"Error preprocessing row: {e}")
    
    def _safe_decimal(self, value):
        """Safely convert a value to Decimal"""
        if value is None or value == '':
            return None
        try:
            if isinstance(value, str):
                value = value.replace(',', '.')
            return decimal.Decimal(str(value))
        except (ValueError, decimal.InvalidOperation, TypeError):
            return None