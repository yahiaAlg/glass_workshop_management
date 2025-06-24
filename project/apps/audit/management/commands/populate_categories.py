# management/commands/populate_categories.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from ...models import ExpenseCategory, RevenueCategory, AdditionalExpense, AdditionalRevenue

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate expense and revenue categories with sample data'

    def handle(self, *args, **options):
        # Get or create a user for sample data
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True}
        )
        
        # Create expense categories
        expense_categories = [
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
        
        created_expense_cats = {}
        for code, name in expense_categories:
            cat, created = ExpenseCategory.objects.get_or_create(name=code)
            created_expense_cats[code] = cat
        
        # Create revenue categories
        revenue_categories = [
            ('RECYCLING', 'Recyclage de verre'),
            ('WASTE_SALE', 'Vente de déchets'),
            ('EQUIPMENT_RENTAL', 'Location d\'équipement'),
            ('TRAINING', 'Formation et consultation'),
            ('REPAIR_SERVICE', 'Services de réparation'),
            ('OTHER', 'Autres revenus')
        ]
        
        created_revenue_cats = {}
        for code, name in revenue_categories:
            cat, created = RevenueCategory.objects.get_or_create(name=code)
            created_revenue_cats[code] = cat
        
        # Sample expenses
        sample_expenses = [
            {
                'title': 'Salaires équipe janvier',
                'description': 'Paiement des salaires de l\'équipe pour janvier',
                'category': created_expense_cats['PAYROLL'],
                'amount': Decimal('15000.00'),
                'date': date.today() - timedelta(days=30),
                'status': 'PAID',
                'vendor': 'Employés',
                'reference_number': 'PAY-2024-001'
            },
            {
                'title': 'Achat équipement de tri',
                'description': 'Nouveau système de tri automatique',
                'category': created_expense_cats['EQUIPMENT'],
                'amount': Decimal('8500.00'),
                'date': date.today() - timedelta(days=15),
                'status': 'APPROVED',
                'vendor': 'TechSort Industries',
                'reference_number': 'EQ-2024-003'
            },
            {
                'title': 'Maintenance camions',
                'description': 'Révision et réparation des véhicules de collecte',
                'category': created_expense_cats['MAINTENANCE'],
                'amount': Decimal('2800.00'),
                'date': date.today() - timedelta(days=7),
                'status': 'PENDING',
                'vendor': 'Garage Central',
                'reference_number': 'MAINT-2024-012'
            },
            {
                'title': 'Facture électricité',
                'description': 'Consommation électrique centre de tri',
                'category': created_expense_cats['UTILITIES'],
                'amount': Decimal('1200.00'),
                'date': date.today() - timedelta(days=5),
                'status': 'PAID',
                'vendor': 'Sonelgaz',
                'reference_number': 'ELEC-2024-02'
            }
        ]
        
        for expense_data in sample_expenses:
            AdditionalExpense.objects.get_or_create(
                reference_number=expense_data['reference_number'],
                defaults={**expense_data, 'created_by': user}
            )
        
        # Sample revenues
        sample_revenues = [
            {
                'title': 'Vente verre recyclé',
                'description': 'Vente de 5 tonnes de verre recyclé',
                'category': created_revenue_cats['RECYCLING'],
                'amount': Decimal('3500.00'),
                'date': date.today() - timedelta(days=20),
                'status': 'RECEIVED',
                'client': 'Verrerie Algérienne',
                'reference_number': 'REC-2024-008'
            },
            {
                'title': 'Location équipement BTP',
                'description': 'Location de conteneurs pour chantier',
                'category': created_revenue_cats['EQUIPMENT_RENTAL'],
                'amount': Decimal('2200.00'),
                'date': date.today() - timedelta(days=10),
                'status': 'CONFIRMED',
                'client': 'Entreprise BTP Sétif',
                'reference_number': 'LOC-2024-015'
            },
            {
                'title': 'Formation gestion déchets',
                'description': 'Formation pour municipalité voisine',
                'category': created_revenue_cats['TRAINING'],
                'amount': Decimal('4800.00'),
                'date': date.today() - timedelta(days=3),
                'status': 'PENDING',
                'client': 'Mairie de Béjaïa',
                'reference_number': 'FORM-2024-003'
            },
            {
                'title': 'Vente matériaux recyclés',
                'description': 'Vente de plastique et métaux récupérés',
                'category': created_revenue_cats['WASTE_SALE'],
                'amount': Decimal('1800.00'),
                'date': date.today() - timedelta(days=1),
                'status': 'RECEIVED',
                'client': 'RecyclePlast DZ',
                'reference_number': 'MAT-2024-021'
            }
        ]
        
        for revenue_data in sample_revenues:
            AdditionalRevenue.objects.get_or_create(
                reference_number=revenue_data['reference_number'],
                defaults={**revenue_data, 'created_by': user}
            )
        
        self.stdout.write(self.style.SUCCESS('Categories, expenses, and revenues populated successfully'))