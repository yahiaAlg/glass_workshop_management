# apps/inventory/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget
from .models import GlassProduct

class GlassProductResource(resources.ModelResource):
    supplier = fields.Field(
        column_name='supplier',
        attribute='supplier',
        widget=ForeignKeyWidget('suppliers.Supplier', 'name')
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
        model = GlassProduct
        fields = (
            'id', 'code', 'name', 'description', 'glass_type', 'thickness',
            'color', 'finish', 'unit', 'cost_price', 'selling_price',
            'stock_quantity', 'minimum_stock', 'supplier', 'category',
            'status', 'created_at', 'updated_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'