from django.db import models

class Customer(models.Model):
    CUSTOMER_TYPES = [
        ('individual', 'Particulier'),
        ('commercial', 'Entreprise'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom/Raison sociale")
    customer_type = models.CharField(max_length=12, choices=CUSTOMER_TYPES, default='individual', verbose_name="Type")
    address = models.TextField(verbose_name="Adresse")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    
    # Legal identifiers for commercial clients
    nis = models.CharField(max_length=50, blank=True, verbose_name="NIS")
    rc = models.CharField(max_length=50, blank=True, verbose_name="RC")
    art = models.CharField(max_length=50, blank=True, verbose_name="ART")
    
    contact_person = models.CharField(max_length=200, blank=True, verbose_name="Personne de contact")
    payment_terms = models.CharField(max_length=100, default="Paiement à la livraison", verbose_name="Conditions de paiement")
    notes = models.TextField(blank=True, verbose_name="Notes")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_total_purchases(self):
        from apps.invoices.models import Invoice
        return Invoice.objects.filter(customer=self).aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0