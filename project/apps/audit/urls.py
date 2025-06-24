from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/edit/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Revenues
    path('revenues/', views.revenue_list, name='revenue_list'),
    path('revenues/create/', views.revenue_create, name='revenue_create'),
    path('revenues/<int:pk>/', views.revenue_detail, name='revenue_detail'),
    path('revenues/<int:pk>/edit/', views.revenue_update, name='revenue_update'),
    path('revenues/<int:pk>/delete/', views.revenue_delete, name='revenue_delete'),
    
    # Documents
    path('upload/<str:type>/<int:pk>/', views.upload_document, name='upload_document'),
    
    # API endpoints for charts
    path('api/expense-chart/', views.expense_chart_data, name='expense_chart_data'),
    path('api/revenue-chart/', views.revenue_chart_data, name='revenue_chart_data'),
]
