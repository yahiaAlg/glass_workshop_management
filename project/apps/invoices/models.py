from django.db import models
from django.contrib.auth import get_user_model
from apps.customers.models import Customer
from apps.inventory.models import GlassProduct
from apps.orders.models import Order

User = get_user_model()

class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Espèces'),
        ('card', 'Carte bancaire'),
        ('cheque', 'Chèque'),
        ('transfer', 'Virement'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de facture")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Client")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Commande")
    
    invoice_date = models.DateField(auto_now_add=True, verbose_name="Date de facture")
    due_date = models.DateField(verbose_name="Date d'échéance")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash', verbose_name="Mode de paiement")
    
    delivery_address = models.TextField(blank=True, verbose_name="Adresse de livraison")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Date de livraison")
    installation_notes = models.TextField(blank=True, verbose_name="Notes d'installation")
    warranty_info = models.TextField(blank=True, verbose_name="Informations de garantie")
    
    # Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Sous-total")
    services_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total services")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Remise")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant TVA")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Créée par")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        from datetime import datetime
        year = datetime.now().year
        prefix = f"GLS-{year}-"
        last_invoice = Invoice.objects.filter(invoice_number__startswith=prefix).order_by('-id').first()
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"{prefix}{new_number:04d}"
    
    def calculate_totals(self):
        from apps.company.models import Company
        
        # Calculate product subtotal
        self.subtotal = sum(item.subtotal for item in self.invoiceitem_set.all())
        
        # Calculate services total
        self.services_total = sum(service.amount for service in self.invoiceservice_set.all())
        
        # Calculate tax
        company = Company.objects.first()
        tax_rate = company.tax_rate if company else 19.00
        taxable_amount = self.subtotal + self.services_total - self.discount_amount
        self.tax_amount = (taxable_amount * tax_rate) / 100
        
        # Calculate total
        self.total_amount = taxable_amount + self.tax_amount
        
        self.save()

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Facture")
    product = models.ForeignKey(GlassProduct, on_delete=models.CASCADE, verbose_name="Produit")
    description = models.TextField(verbose_name="Description")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sous-total")
    
    # Glass specifications
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Largeur (cm)")
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Hauteur (cm)")
    thickness = models.CharField(max_length=10, blank=True, verbose_name="Épaisseur")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Article de facture"
        verbose_name_plural = "Articles de facture"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.invoice.calculate_totals()

class InvoiceService(models.Model):
    SERVICE_TYPES = [
        ('delivery', 'Livraison'),
        ('installation', 'Installation'),
        ('cutting', 'Découpe'),
        ('packaging', 'Emballage'),
        ('other', 'Autre'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Facture")
    service_type = models.CharField(max_length=15, choices=SERVICE_TYPES, verbose_name="Type de service")
    description = models.CharField(max_length=200, verbose_name="Description")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Service de facture"
        verbose_name_plural = "Services de facture"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.calculate_totals()

class Payment(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Terminé'),
        ('pending', 'En attente'),
        ('failed', 'Échoué'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Facture")
    payment_date = models.DateField(verbose_name="Date de paiement")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant")
    payment_method = models.CharField(max_length=10, choices=Invoice.PAYMENT_METHODS, verbose_name="Mode de paiement")
    reference = models.CharField(max_length=50, blank=True, verbose_name="Référence")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Paiement {self.invoice.invoice_number} - {self.amount}€"