from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from apps.company.models import Company
from apps.customers.models import Customer
from apps.inventory.models import GlassProduct
from apps.suppliers.models import Supplier
from apps.orders.models import Order, OrderItem
from apps.invoices.models import Invoice, InvoiceItem, InvoiceService, Payment

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data for glass business'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Creating sample data...')
        
        # Create company
        company = self.create_company()
        
        # Create users
        users = self.create_users()
        
        # Create suppliers
        suppliers = self.create_suppliers()
        
        # Create glass products
        products = self.create_glass_products(suppliers)
        
        # Create customers
        customers = self.create_customers()
        
        # # Create orders
        # orders = self.create_orders(customers, products)
        
        # # Create invoices
        # invoices = self.create_invoices(customers, products, orders, users)
        
        # # Create payments
        # self.create_payments(invoices)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created sample data:')
        )
        self.stdout.write(f'- Company: {Company.objects.count()}')
        self.stdout.write(f'- Users: {User.objects.count()}')
        self.stdout.write(f'- Suppliers: {Supplier.objects.count()}')
        self.stdout.write(f'- Products: {GlassProduct.objects.count()}')
        self.stdout.write(f'- Customers: {Customer.objects.count()}')
        # self.stdout.write(f'- Orders: {Order.objects.count()}')
        # self.stdout.write(f'- Invoices: {Invoice.objects.count()}')
        # self.stdout.write(f'- Payments: {Payment.objects.count()}')

    def clear_data(self):
        """Clear all existing data"""
        Payment.objects.all().delete()
        InvoiceService.objects.all().delete()
        InvoiceItem.objects.all().delete()
        Invoice.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        GlassProduct.objects.all().delete()
        Customer.objects.all().delete()
        Supplier.objects.all().delete()
        Company.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_company(self):
        """Create sample company"""
        company, created = Company.objects.get_or_create(
            name="Cristal Glass Pro",
            defaults={
                'business_type': "Commerce de verre et installation",
                'address': "123 Rue du Verre, 19000 Sétif, Algérie",
                'phone': "+213 36 123 456",
                'fax': "+213 36 123 457",
                'email': "contact@cristalglassPro.dz",
                'website': "www.cristalglassPro.dz",
                'rc': "19/00123456",
                'art': "19123456789",
                'nis': "000019123456789",
                'nif': "000019123456789",
                'rib': "00710123456789012345",
                'capital_social': Decimal('2000000.00'),
                'tax_rate': Decimal('19.00'),
                'operating_hours': "Lundi-Vendredi: 8h-17h, Samedi: 8h-12h",
                'certifications': "ISO 9001, Certification installation verre sécurisé"
            }
        )
        return company

    def create_users(self):
        """Create sample users"""
        users = []
        
        # Admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@cristalglassPro.dz',
                'first_name': 'Ahmed',
                'last_name': 'Benali',
                'role': 'admin',
                'phone': '+213 555 123 456',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        users.append(admin)
        
        # Worker users
        worker_data = [
            ('karim', 'Karim', 'Mansouri', 'karim@cristalglassPro.dz', '+213 555 234 567'),
            ('fatima', 'Fatima', 'Boudjemaa', 'fatima@cristalglassPro.dz', '+213 555 345 678'),
            ('omar', 'Omar', 'Zerrouk', 'omar@cristalglassPro.dz', '+213 555 456 789'),
        ]
        
        for username, first_name, last_name, email, phone in worker_data:
            worker, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'worker',
                    'phone': phone,
                    'is_staff': True
                }
            )
            if created:
                worker.set_password('worker123')
                worker.save()
            users.append(worker)
        
        return users

    def create_suppliers(self):
        """Create sample suppliers"""
        suppliers_data = [
            {
                'name': 'Verre Algérie SARL',
                'contact_person': 'Samir Abdellah',
                'phone': '+213 21 123 456',
                'email': 'contact@verrealg.dz',
                'address': 'Zone Industrielle, Alger',
                'payment_terms': '30 jours',
                'notes': 'Fournisseur principal de verre standard'
            },
            {
                'name': 'Guardian Glass Algérie',
                'contact_person': 'Nadia Bensalem',
                'phone': '+213 31 234 567',
                'email': 'n.bensalem@guardian.dz',
                'address': 'Route Nationale, Oran',
                'payment_terms': '45 jours',
                'notes': 'Spécialiste verre haute qualité et sécurisé'
            },
            {
                'name': 'Cristal Import',
                'contact_person': 'Youcef Hamadi',
                'phone': '+213 25 345 678',
                'email': 'y.hamadi@cristalimport.dz',
                'address': 'Rue de l\'Industrie, Constantine',
                'payment_terms': '15 jours',
                'notes': 'Import de verre décoratif'
            }
        ]
        
        suppliers = []
        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            suppliers.append(supplier)
        
        return suppliers

    def create_glass_products(self, suppliers):
        """Create sample glass products"""
        products_data = [
            {
                'name': 'Verre Clair Standard',
                'glass_type': 'window',
                'thickness': '4',
                'color': 'clear',
                'finish': 'polished',
                'cost_price': Decimal('850.00'),
                'selling_price': Decimal('1200.00'),
                'stock_quantity': Decimal('50.00'),
                'description': 'Verre de fenêtre standard 4mm'
            },
            {
                'name': 'Verre Clair Épais',
                'glass_type': 'window',
                'thickness': '6',
                'color': 'clear',
                'finish': 'polished',
                'cost_price': Decimal('1200.00'),
                'selling_price': Decimal('1650.00'),
                'stock_quantity': Decimal('30.00'),
                'description': 'Verre de fenêtre épais 6mm'
            },
            {
                'name': 'Miroir Argent',
                'glass_type': 'mirror',
                'thickness': '4',
                'color': 'clear',
                'finish': 'polished',
                'cost_price': Decimal('1500.00'),
                'selling_price': Decimal('2100.00'),
                'stock_quantity': Decimal('25.00'),
                'description': 'Miroir argenté 4mm'
            },
            {
                'name': 'Verre Trempé Sécurisé',
                'glass_type': 'tempered',
                'thickness': '8',
                'color': 'clear',
                'finish': 'polished',
                'cost_price': Decimal('2800.00'),
                'selling_price': Decimal('3800.00'),
                'stock_quantity': Decimal('15.00'),
                'description': 'Verre trempé sécurisé 8mm'
            },
            {
                'name': 'Verre Douche Dépoli',
                'glass_type': 'shower',
                'thickness': '6',
                'color': 'clear',
                'finish': 'frosted',
                'cost_price': Decimal('1800.00'),
                'selling_price': Decimal('2500.00'),
                'stock_quantity': Decimal('20.00'),
                'description': 'Verre dépoli pour douche 6mm'
            },
            {
                'name': 'Plateau de Table Épais',
                'glass_type': 'table',
                'thickness': '12',
                'color': 'clear',
                'finish': 'polished',
                'unit': 'piece',
                'cost_price': Decimal('4500.00'),
                'selling_price': Decimal('6200.00'),
                'stock_quantity': Decimal('8.00'),
                'description': 'Plateau de table en verre 12mm'
            },
            {
                'name': 'Verre Décoratif Bronze',
                'glass_type': 'decorative',
                'thickness': '5',
                'color': 'bronze',
                'finish': 'polished',
                'cost_price': Decimal('1600.00'),
                'selling_price': Decimal('2200.00'),
                'stock_quantity': Decimal('12.00'),
                'description': 'Verre décoratif teinté bronze 5mm'
            },
            {
                'name': 'Verre Feuilleté Sécurité',
                'glass_type': 'laminated',
                'thickness': '10',
                'color': 'clear',
                'finish': 'polished',
                'cost_price': Decimal('3200.00'),
                'selling_price': Decimal('4300.00'),
                'stock_quantity': Decimal('10.00'),
                'description': 'Verre feuilleté sécurisé 10mm'
            }
        ]
        
        products = []
        for i, data in enumerate(products_data):
            data['supplier'] = suppliers[i % len(suppliers)]
            product, created = GlassProduct.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            products.append(product)
        
        return products

    def create_customers(self):
        """Create sample customers"""
        customers_data = [
            {
                'name': 'Maison Benaissa',
                'customer_type': 'individual',
                'address': '15 Rue des Oliviers, Sétif',
                'phone': '+213 555 111 222',
                'email': 'benaissa@email.dz',
                'payment_terms': 'Paiement à la livraison',
                'notes': 'Client fidèle depuis 2020'
            },
            {
                'name': 'Entreprise Moderne SARL',
                'customer_type': 'commercial',
                'address': 'Zone d\'Activité, Sétif',
                'phone': '+213 36 111 333',
                'email': 'contact@moderne.dz',
                'nis': '000019111333444',
                'rc': '19/00111333',
                'art': '19111333444',
                'contact_person': 'Mme Zahra Lakhal',
                'payment_terms': '30 jours',
                'notes': 'Commandes régulières'
            },
            {
                'name': 'Villa Meziani',
                'customer_type': 'individual',
                'address': '42 Cité El Hidhab, Sétif',
                'phone': '+213 555 222 333',
                'email': 'meziani.villa@email.dz',
                'payment_terms': 'Paiement comptant',
                'notes': 'Projet de rénovation en cours'
            },
            {
                'name': 'Hôtel Panorama',
                'customer_type': 'commercial',
                'address': 'Centre Ville, Sétif',
                'phone': '+213 36 222 444',
                'email': 'direction@panorama-hotel.dz',
                'nis': '000019222444555',
                'rc': '19/00222444',
                'art': '19222444555',
                'contact_person': 'M. Tarek Boudiaf',
                'payment_terms': '45 jours',
                'notes': 'Rénovation complète de l\'hôtel'
            },
            {
                'name': 'Résidence Benali',
                'customer_type': 'individual',
                'address': '8 Rue du Parc, Sétif',
                'phone': '+213 555 333 444',
                'email': 'benali.residence@email.dz',
                'payment_terms': 'Paiement à la livraison',
                'notes': 'Construction neuve'
            }
        ]
        
        customers = []
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            customers.append(customer)
        
        return customers

    # def create_orders(self, customers, products):
    #     """Create sample orders"""
    #     orders = []
        
    #     for i in range(8):
    #         customer = random.choice(customers)
    #         order_date = timezone.now() - timedelta(days=random.randint(1, 30))
    #         delivery_date = order_date.date() + timedelta(days=random.randint(5, 15))
            
    #         order = Order.objects.create(
    #             customer=customer,
    #             delivery_date=delivery_date,
    #             status=random.choice(['pending', 'confirmed', 'delivered']),
    #             delivery_address=customer.address,
    #             installation_required=random.choice([True, False]),
    #             notes=random.choice([
    #                 'Livraison matin de préférence',
    #                 'Appeler avant livraison',
    #                 'Accès difficile - prévoir aide',
    #                 ''
    #             ])
    #         )
    #         order.created_at = order_date
    #         order.save()
            
    #         # Add order items
    #         num_items = random.randint(1, 4)
    #         selected_products = random.sample(products, min(num_items, len(products)))
            
    #         for product in selected_products:
    #             quantity = Decimal(str(random.uniform(1, 10))).quantize(Decimal('0.01'))
    #             width = Decimal(str(random.randint(80, 200)))  # Width in cm
    #             height = Decimal(str(random.randint(100, 250)))  # Height in cm
                
    #             OrderItem.objects.create(
    #                 order=order,
    #                 product=product,
    #                 width=width,
    #                 height=height,
    #                 quantity=quantity,
    #                 unit_price=product.selling_price,
    #                 notes=random.choice(['', 'Découpe sur mesure', 'Installation incluse'])
    #             )
            
    #         orders.append(order)
        
    #     return orders

    # def create_invoices(self, customers, products, orders, users):
    #     """Create sample invoices"""
    #     invoices = []
        
    #     # Create invoices from orders
    #     for order in orders[:5]:
    #         invoice_date = order.created_at.date() + timedelta(days=random.randint(1, 5))
    #         due_date = invoice_date + timedelta(days=30)
            
    #         invoice = Invoice.objects.create(
    #             customer=order.customer,
    #             order=order,
    #             due_date=due_date,
    #             payment_method=random.choice(['cash', 'card', 'transfer']),
    #             delivery_address=order.delivery_address,
    #             delivery_date=order.delivery_date,
    #             installation_notes=random.choice([
    #                 'Installation prévue le matin',
    #                 'Équipe de 2 personnes',
    #                 'Matériel spécialisé requis',
    #                 ''
    #             ]),
    #             warranty_info='Garantie 2 ans sur le verre, 1 an sur l\'installation',
    #             status=random.choice(['draft', 'sent', 'paid']),
    #             notes=random.choice(['', 'Client VIP', 'Remise accordée']),
    #             created_by=random.choice(users)
    #         )
    #         invoice.invoice_date = invoice_date
    #         invoice.save()
            
    #         # Add invoice items from order items
    #         for order_item in order.orderitem_set.all():
    #             InvoiceItem.objects.create(
    #                 invoice=invoice,
    #                 product=order_item.product,
    #                 description=f"{order_item.product.name} - {order_item.product.thickness}mm",
    #                 quantity=order_item.quantity,
    #                 unit_price=order_item.unit_price,
    #                 width=Decimal(str(random.randint(80, 200))),
    #                 height=Decimal(str(random.randint(100, 250))),
    #                 thickness=order_item.product.thickness + 'mm'
    #             )
            
    #         # Add services
    #         if order.installation_required:
    #             InvoiceService.objects.create(
    #                 invoice=invoice,
    #                 service_type='installation',
    #                 description='Installation sur site',
    #                 amount=Decimal('5000.00')
    #             )
            
    #         InvoiceService.objects.create(
    #             invoice=invoice,
    #             service_type='delivery',
    #             description='Livraison',
    #             amount=Decimal('2000.00')
    #         )
            
    #         # Add random discount
    #         if random.random() < 0.3:  # 30% chance of discount
    #             invoice.discount_amount = Decimal(str(random.randint(500, 2000)))
    #             invoice.save()
            
    #         invoices.append(invoice)
        
    #     # Create standalone invoices
    #     for i in range(3):
    #         customer = random.choice(customers)
    #         invoice_date = date.today() - timedelta(days=random.randint(1, 60))
    #         due_date = invoice_date + timedelta(days=30)
            
    #         invoice = Invoice.objects.create(
    #             customer=customer,
    #             due_date=due_date,
    #             payment_method=random.choice(['cash', 'card', 'cheque']),
    #             delivery_address=customer.address,
    #             warranty_info='Garantie standard 2 ans',
    #             status=random.choice(['sent', 'paid', 'overdue']),
    #             created_by=random.choice(users)
    #         )
    #         invoice.invoice_date = invoice_date
    #         invoice.save()
            
    #         # Add invoice items
    #         num_items = random.randint(1, 3)
    #         selected_products = random.sample(products, min(num_items, len(products)))
            
    #         for product in selected_products:
    #             quantity = Decimal(str(random.uniform(1, 8))).quantize(Decimal('0.01'))
    #             InvoiceItem.objects.create(
    #                 invoice=invoice,
    #                 product=product,
    #                 description=f"{product.name} sur mesure",
    #                 quantity=quantity,
    #                 unit_price=product.selling_price,
    #                 width=Decimal(str(random.randint(60, 180))),
    #                 height=Decimal(str(random.randint(80, 220))),
    #                 thickness=product.thickness + 'mm'
    #             )
            
    #         invoices.append(invoice)
        
    #     return invoices

    # def create_payments(self, invoices):
    #     """Create sample payments"""
    #     payments = []
        
    #     for invoice in invoices:
    #         if invoice.status in ['paid', 'overdue']:
    #             # Full payment
    #             if random.random() < 0.7:  # 70% chance of full payment
    #                 payment = Payment.objects.create(
    #                     invoice=invoice,
    #                     payment_date=invoice.invoice_date + timedelta(days=random.randint(1, 45)),
    #                     amount=invoice.total_amount,
    #                     payment_method=invoice.payment_method,
    #                     reference=f"REF{random.randint(100000, 999999)}",
    #                     status='completed',
    #                     notes=random.choice(['', 'Paiement comptant', 'Virement reçu'])
    #                 )
    #                 payments.append(payment)
    #             else:
    #                 # Partial payments
    #                 remaining = invoice.total_amount
    #                 num_payments = random.randint(2, 3)
                    
    #                 for i in range(num_payments):
    #                     if i == num_payments - 1:
    #                         # Last payment - remaining amount
    #                         amount = remaining
    #                     else:
    #                         # Partial payment
    #                         amount = remaining * Decimal(str(random.uniform(0.3, 0.6)))
    #                         remaining -= amount
                        
    #                     payment = Payment.objects.create(
    #                         invoice=invoice,
    #                         payment_date=invoice.invoice_date + timedelta(days=random.randint(1, 60)),
    #                         amount=amount,
    #                         payment_method=random.choice(['cash', 'card', 'transfer']),
    #                         reference=f"REF{random.randint(100000, 999999)}",
    #                         status='completed',
    #                         notes=f'Paiement partiel {i+1}/{num_payments}'
    #                     )
    #                     payments.append(payment)
        
    #     return payments
    
"""
touch project/apps/{authentication,company,customers,dashboard,inventory,invoices,orders,suppliers}/admin.py
"""