# apps/suppliers/resources.py
from import_export import resources, fields
from import_export.widgets import DateWidget
from .models import Supplier

class SupplierResource(resources.ModelResource):
    last_order_date = fields.Field(
        attribute='last_order_date',
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
        model = Supplier
        fields = (
            'id', 'name', 'contact_person', 'phone', 'email', 'address',
            'payment_terms', 'notes', 'status', 'last_order_date',
            'created_at', 'updated_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'