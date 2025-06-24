from django.db import models
from apps.authentication.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class ExpenseCategory(models.Model):
    CATEGORY_CHOICES = [
        ('PAYROLL', 'Paiements des employés'),
        ('EQUIPMENT', 'Charges d\'équipement'),
        ('MAINTENANCE', 'Charges de maintenance'),
        ('UTILITIES', 'Électricité/Eau/Gaz'),
        ('MATERIALS', 'Matériaux et fournitures'),
        ('TRANSPORT', 'Transport et livraison'),
        ('INSURANCE', 'Assurances'),
        ('TAXES', 'Taxes et impôts'),
        ('OTHER', 'Autres charges')
    ]
    
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Catégorie de dépense"
        verbose_name_plural = "Catégories de dépenses"
    
    def __str__(self):
        return self.get_name_display()

class RevenueCategory(models.Model):
    CATEGORY_CHOICES = [
        ('RECYCLING', 'Recyclage de verre'),
        ('WASTE_SALE', 'Vente de déchets'),
        ('EQUIPMENT_RENTAL', 'Location d\'équipement'),
        ('TRAINING', 'Formation et consultation'),
        ('REPAIR_SERVICE', 'Services de réparation'),
        ('OTHER', 'Autres revenus')
    ]
    
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Catégorie de revenu"
        verbose_name_plural = "Catégories de revenus"
    
    def __str__(self):
        return self.get_name_display()

class AdditionalExpense(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('PAID', 'Payé'),
        ('CANCELLED', 'Annulé')
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, verbose_name="Catégorie")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Montant")
    date = models.DateField(verbose_name="Date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Statut")
    vendor = models.CharField(max_length=200, blank=True, verbose_name="Fournisseur/Bénéficiaire")
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="Numéro de référence")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Dépense additionnelle"
        verbose_name_plural = "Dépenses additionnelles"
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.amount}€"

class AdditionalRevenue(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmé'),
        ('RECEIVED', 'Reçu'),
        ('CANCELLED', 'Annulé')
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    category = models.ForeignKey(RevenueCategory, on_delete=models.CASCADE, verbose_name="Catégorie")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Montant")
    date = models.DateField(verbose_name="Date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Statut")
    client = models.CharField(max_length=200, blank=True, verbose_name="Client/Source")
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="Numéro de référence")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Revenu additionnel"
        verbose_name_plural = "Revenus additionnels"
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.amount}€"

def expense_upload_path(instance, filename):
    return f'audit/expenses/{instance.expense.id}/{filename}'

def revenue_upload_path(instance, filename):
    return f'audit/revenues/{instance.revenue.id}/{filename}'

class ExpenseDocument(models.Model):
    expense = models.ForeignKey(AdditionalExpense, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to=expense_upload_path, verbose_name="Fichier")
    name = models.CharField(max_length=200, verbose_name="Nom du document")
    description = models.TextField(blank=True, verbose_name="Description")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Document de dépense"
        verbose_name_plural = "Documents de dépenses"
    
    def __str__(self):
        return f"{self.name} - {self.expense.title}"

class RevenueDocument(models.Model):
    revenue = models.ForeignKey(AdditionalRevenue, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to=revenue_upload_path, verbose_name="Fichier")
    name = models.CharField(max_length=200, verbose_name="Nom du document")
    description = models.TextField(blank=True, verbose_name="Description")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Document de revenu"
        verbose_name_plural = "Documents de revenus"
    
    def __str__(self):
        return f"{self.name} - {self.revenue.title}"