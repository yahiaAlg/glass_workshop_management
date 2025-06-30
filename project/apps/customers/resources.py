# apps/customers/resources.py
from import_export import resources, fields
from import_export.widgets import DateWidget
from .models import Customer

class CustomerResource(resources.ModelResource):
    created_at = fields.Field(
        attribute='created_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    updated_at = fields.Field(
        attribute='updated_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    class Meta:
        model = Customer
        fields = (
            'id', 'name', 'customer_type', 'address', 'phone', 'email',
            'nis', 'rc', 'art', 'contact_person', 'payment_terms',
            'notes', 'status', 'created_at', 'updated_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'