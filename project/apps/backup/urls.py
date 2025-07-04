from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.BackupListView.as_view(), name='list'),
    path('create/', views.create_backup, name='create'),
    path('restore/', views.restore_backup, name='restore'),
    path('restore-from-backup/', views.restore_from_backup, name='restore_from_backup'),
    path('download/<int:backup_id>/', views.download_backup, name='download'),
    path('delete/<int:backup_id>/', views.delete_backup, name='delete'),
    path('status/<int:backup_id>/', views.backup_status, name='status'),
]