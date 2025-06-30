# apps/audit/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget
from .models import (
    ExpenseCategory, RevenueCategory, AdditionalExpense, 
    AdditionalRevenue
)

class ExpenseCategoryResource(resources.ModelResource):
    created_at = fields.Field(
        attribute='created_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    class Meta:
        model = ExpenseCategory
        fields = ('id', 'name', 'description', 'is_active', 'created_at')
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'

class RevenueCategoryResource(resources.ModelResource):
    created_at = fields.Field(
        attribute='created_at',
        widget=DateWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    class Meta:
        model = RevenueCategory
        fields = ('id', 'name', 'description', 'is_active', 'created_at')
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'

class AdditionalExpenseResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget('audit.ExpenseCategory', 'name')
    )
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget('authentication.User', 'username')
    )
    date = fields.Field(
        attribute='date',
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
        model = AdditionalExpense
        fields = (
            'id', 'title', 'description', 'category', 'amount', 'date',
            'status', 'vendor', 'reference_number', 'created_by',
            'notes', 'created_at', 'updated_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'

class AdditionalRevenueResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget('audit.RevenueCategory', 'name')
    )
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget('authentication.User', 'username')
    )
    date = fields.Field(
        attribute='date',
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
        model = AdditionalRevenue
        fields = (
            'id', 'title', 'description', 'category', 'amount', 'date',
            'status', 'client', 'reference_number', 'created_by',
            'notes', 'created_at', 'updated_at'
        )
        export_order = fields
        import_id_fields = ('id',)
        date_field = 'created_at'