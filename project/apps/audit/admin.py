from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
from .resources import (
    ExpenseCategoryResource, RevenueCategoryResource,
    AdditionalExpenseResource, AdditionalRevenueResource
)

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(ImportExportModelAdmin):
    resource_class = ExpenseCategoryResource
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'name']

@admin.register(RevenueCategory)
class RevenueCategoryAdmin(ImportExportModelAdmin):
    resource_class = RevenueCategoryResource
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'name']

class ExpenseDocumentInline(admin.TabularInline):
    model = ExpenseDocument
    extra = 0

@admin.register(AdditionalExpense)
class AdditionalExpenseAdmin(ImportExportModelAdmin):
    resource_class = AdditionalExpenseResource
    list_display = ['title', 'category', 'amount', 'date', 'status', 'created_by']
    list_filter = ['status', 'category', 'date', 'created_at']
    search_fields = ['title', 'description', 'vendor']
    inlines = [ExpenseDocumentInline]
    readonly_fields = ['created_at', 'updated_at']

class RevenueDocumentInline(admin.TabularInline):
    model = RevenueDocument
    extra = 0

@admin.register(AdditionalRevenue)
class AdditionalRevenueAdmin(ImportExportModelAdmin):
    resource_class = AdditionalRevenueResource
    list_display = ['title', 'category', 'amount', 'date', 'status', 'created_by']
    list_filter = ['status', 'category', 'date', 'created_at']
    search_fields = ['title', 'description', 'client']
    inlines = [RevenueDocumentInline]
    readonly_fields = ['created_at', 'updated_at']