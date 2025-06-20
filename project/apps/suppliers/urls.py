from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='list'),
    path('create/', views.supplier_create, name='create'),
    path('<int:pk>/', views.supplier_detail, name='detail'),
    path('<int:pk>/edit/', views.supplier_edit, name='edit'),
    path('<int:pk>/delete/', views.supplier_delete, name='delete'),
]