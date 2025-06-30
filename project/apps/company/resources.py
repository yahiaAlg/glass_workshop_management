# apps/company/resources.py
from import_export import resources, fields
from import_export.widgets import DateWidget
from .models import Company

class CompanyResource(resources.ModelResource):
    created_at = fields.Field(
        attribute='created_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    updated_at = fields.Field(
        attribute='updated_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    class Meta:
        model = Company
        fields = (
            'id', 'name', 'business_type', 'address', 'phone', 'fax', 'email',
            'website', 'rc', 'art', 'nis', 'nif', 'rib', 'capital_social',
            'tax_rate', 'operating_hours', 'certifications', 'created_at', 'updated_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'