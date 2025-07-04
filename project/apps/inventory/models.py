from django.db import models

class GlassProduct(models.Model):
    GLASS_TYPES = [
        ('window', 'Verre de fenêtre'),
        ('mirror', 'Miroir'),
        ('shower', 'Verre de douche'),
        ('table', 'Plateau de table'),
        ('decorative', 'Verre décoratif'),
        ('security', 'Verre sécurisé'),
        ('tempered', 'Verre trempé'),
        ('laminated', 'Verre feuilleté'),
    ]
    
    THICKNESS_CHOICES = [
        ('3', '3mm'),
        ('4', '4mm'),
        ('5', '5mm'),
        ('6', '6mm'),
        ('8', '8mm'),
        ('10', '10mm'),
        ('12', '12mm'),
        ('15', '15mm'),
        ('19', '19mm'),
    ]
    
    COLOR_CHOICES = [
        ('clear', 'Transparent'),
        ('bronze', 'Bronze'),
        ('grey', 'Gris'),
        ('green', 'Vert'),
        ('blue', 'Bleu'),
        ('black', 'Noir'),
    ]
    
    FINISH_CHOICES = [
        ('polished', 'Poli'),
        ('frosted', 'Dépoli'),
        ('textured', 'Texturé'),
        ('sandblasted', 'Sablé'),
    ]
    
    UNIT_CHOICES = [
        ('sqm', 'Mètre carré'),
        ('piece', 'Pièce'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
    ]
    
    code = models.CharField(max_length=20, unique=True, verbose_name="Code produit")
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    description = models.TextField(blank=True, verbose_name="Description")
    glass_type = models.CharField(max_length=20, choices=GLASS_TYPES, verbose_name="Type de verre")
    thickness = models.CharField(max_length=3, choices=THICKNESS_CHOICES, verbose_name="Épaisseur")
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='clear', verbose_name="Couleur")
    finish = models.CharField(max_length=15, choices=FINISH_CHOICES, default='polished', verbose_name="Finition")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='sqm', verbose_name="Unité de mesure")
    
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
        return f"{self.name} - {self.thickness}mm"
    
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