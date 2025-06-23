from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard_home, name='home'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports'),
    path('reports/sales/', views.sales_reports, name='sales_reports'),
    path('reports/inventory/', views.inventory_reports, name='inventory_reports'),
    path('reports/financial/', views.financial_reports, name='financial_reports'),
    path('reports/customers/', views.customer_reports, name='customer_reports'),
    
    # Export endpoints
    path('exports/sales/excel/', views.export_sales_excel, name='export_sales_excel'),
    path('exports/inventory/excel/', views.export_inventory_excel, name='export_inventory_excel'),
    path('exports/customers/csv/', views.export_customers_csv, name='export_customers_csv'),
    path('exports/financial/pdf/', views.export_financial_pdf, name='export_financial_pdf'),
    
    # API endpoints for charts
    path('api/dashboard-data/', views.dashboard_api_data, name='dashboard_api_data'),
]