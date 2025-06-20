from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('worker', 'Employé'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='worker')
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_worker(self):
        return self.role == 'worker'