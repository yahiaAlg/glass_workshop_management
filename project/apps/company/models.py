from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    business_type = models.CharField(max_length=200, default="Commerce de verre et installation", verbose_name="Type d'activité")
    address = models.TextField(verbose_name="Adresse")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    fax = models.CharField(max_length=20, blank=True, verbose_name="Fax")
    email = models.EmailField(verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Site web")
    
    # Legal identifiers (optional)
    rc = models.CharField(max_length=50, blank=True, verbose_name="RC")
    art = models.CharField(max_length=50, blank=True, verbose_name="ART")
    nis = models.CharField(max_length=50, blank=True, verbose_name="NIS")
    nif = models.CharField(max_length=50, blank=True, verbose_name="NIF")
    rib = models.CharField(max_length=50, blank=True, verbose_name="RIB")
    
    capital_social = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Capital social")
    logo = models.ImageField(upload_to='company/logos/', blank=True, verbose_name="Logo")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=19.00, verbose_name="Taux de TVA (%)")
    operating_hours = models.TextField(blank=True, verbose_name="Heures d'ouverture")
    certifications = models.TextField(blank=True, verbose_name="Certifications")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
    
    def __str__(self):
        return self.name