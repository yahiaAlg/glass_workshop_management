from django.db import models

class GlassType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Type de verre"
        verbose_name_plural = "Types de verre"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class GlassThickness(models.Model):
    value = models.CharField(max_length=3, unique=True)
    display_name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Épaisseur"
        verbose_name_plural = "Épaisseurs"
        ordering = ['value']
    
    def __str__(self):
        return self.display_name

class GlassColor(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Couleur"
        verbose_name_plural = "Couleurs"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class GlassFinish(models.Model):
    code = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Finition"
        verbose_name_plural = "Finitions"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Unit(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Unité de mesure"
        verbose_name_plural = "Unités de mesure"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class GlassProduct(models.Model):
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
    ]
    
    code = models.CharField(max_length=20, unique=True, verbose_name="Code produit")
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Foreign key relationships to dynamic models
    glass_type = models.ForeignKey(GlassType, on_delete=models.PROTECT, verbose_name="Type de verre")
    thickness = models.ForeignKey(GlassThickness, on_delete=models.PROTECT, verbose_name="Épaisseur")
    color = models.ForeignKey(GlassColor, on_delete=models.PROTECT, verbose_name="Couleur")
    finish = models.ForeignKey(GlassFinish, on_delete=models.PROTECT, verbose_name="Finition")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="Unité de mesure")
    
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de revient")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de vente")
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Quantité en stock")
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Stock minimum")
    
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fournisseur")
    category = models.CharField(max_length=100, blank=True, verbose_name="Catégorie")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    image = models.ImageField(upload_to='products/', blank=True, verbose_name="Image")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Produit en verre"
        verbose_name_plural = "Produits en verre"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.thickness.display_name}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    def generate_code(self):
        prefix = "VER"
        last_product = GlassProduct.objects.filter(code__startswith=prefix).order_by('-id').first()
        if last_product:
            last_number = int(last_product.code[3:])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"{prefix}{new_number:04d}"
    
    def is_low_stock(self):
        return self.stock_quantity <= self.minimum_stock
    
    def profit_margin(self):
        if self.cost_price is None or self.selling_price is None or self.cost_price <= 0:
            return 0
        return ((self.selling_price - self.cost_price) / self.cost_price) * 100