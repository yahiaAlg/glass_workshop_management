from django.db import models
from apps.customers.models import Customer
from apps.inventory.models import GlassProduct

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de commande")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Client")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Date de commande")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Date de livraison")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    delivery_address = models.TextField(blank=True, verbose_name="Adresse de livraison")
    installation_required = models.BooleanField(default=False, verbose_name="Installation requise")
    notes = models.TextField(blank=True, verbose_name="Notes")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant total")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        from datetime import datetime
        year = datetime.now().year
        prefix = f"CMD-{year}-"
        last_order = Order.objects.filter(order_number__startswith=prefix).order_by('-id').first()
        if last_order:
            last_number = int(last_order.order_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"{prefix}{new_number:04d}"
    
    def calculate_total(self):
        total = sum(item.subtotal for item in self.orderitem_set.all())
        self.total_amount = total
        self.save()
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Commande")
    product = models.ForeignKey(GlassProduct, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sous-total")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.order.calculate_total()
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"