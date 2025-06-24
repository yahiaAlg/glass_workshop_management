from django.contrib import admin
from .models import *

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'name']

@admin.register(RevenueCategory)
class RevenueCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'name']

class ExpenseDocumentInline(admin.TabularInline):
    model = ExpenseDocument
    extra = 0

@admin.register(AdditionalExpense)
class AdditionalExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'date', 'status', 'created_by']
    list_filter = ['status', 'category', 'date', 'created_at']
    search_fields = ['title', 'description', 'vendor']
    inlines = [ExpenseDocumentInline]
    readonly_fields = ['created_at', 'updated_at']

class RevenueDocumentInline(admin.TabularInline):
    model = RevenueDocument
    extra = 0

@admin.register(AdditionalRevenue)
class AdditionalRevenueAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'date', 'status', 'created_by']
    list_filter = ['status', 'category', 'date', 'created_at']
    search_fields = ['title', 'description', 'client']
    inlines = [RevenueDocumentInline]
    readonly_fields = ['created_at', 'updated_at']