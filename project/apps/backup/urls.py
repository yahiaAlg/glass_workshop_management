# apps/backup/urls.py
from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    path('', views.BackupDashboardView.as_view(), name='dashboard'),
    path('list/', views.backup_list, name='list'),
    path('export/', views.export_data, name='export'),
    path('import/', views.import_data, name='import'),
    path('detail/<int:pk>/', views.backup_detail, name='detail'),
    path('status/<int:pk>/', views.backup_status, name='status'),
    path('download/<int:pk>/', views.download_backup, name='download'),
    path('delete/<int:pk>/', views.delete_backup, name='delete'),
]