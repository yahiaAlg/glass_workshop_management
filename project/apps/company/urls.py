from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('profile/', views.company_profile, name='profile'),
]