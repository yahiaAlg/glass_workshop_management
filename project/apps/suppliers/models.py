from django.db import models

class Supplier(models.Model):
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom du fournisseur")
    contact_person = models.CharField(max_length=200, verbose_name="Personne de contact")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(verbose_name="Adresse")
    payment_terms = models.CharField(max_length=100, default="30 jours", verbose_name="Conditions de paiement")
    notes = models.TextField(blank=True, verbose_name="Notes")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    last_order_date = models.DateField(null=True, blank=True, verbose_name="Dernière commande")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['name']
    
    def __str__(self):
        return self.name