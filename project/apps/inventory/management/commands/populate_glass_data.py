# apps/inventory/management/commands/populate_glass_data.py
from django.core.management.base import BaseCommand
from inventory.models import GlassType, GlassThickness, GlassColor, GlassFinish, Unit

class Command(BaseCommand):
    help = 'Populate glass product reference data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            GlassType.objects.all().delete()
            GlassThickness.objects.all().delete()
            GlassColor.objects.all().delete()
            GlassFinish.objects.all().delete()
            Unit.objects.all().delete()

        # Glass Types
        glass_types = [
            ('window', 'Verre de fenêtre'),
            ('mirror', 'Miroir'),
            ('shower', 'Verre de douche'),
            ('table', 'Plateau de table'),
            ('decorative', 'Verre décoratif'),
            ('security', 'Verre sécurisé'),
            ('tempered', 'Verre trempé'),
            ('laminated', 'Verre feuilleté'),
        ]
        
        for code, name in glass_types:
            GlassType.objects.get_or_create(code=code, defaults={'name': name})

        # Glass Thicknesses
        thicknesses = [
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
        
        for value, display_name in thicknesses:
            GlassThickness.objects.get_or_create(value=value, defaults={'display_name': display_name})

        # Glass Colors
        colors = [
            ('clear', 'Transparent'),
            ('bronze', 'Bronze'),
            ('grey', 'Gris'),
            ('green', 'Vert'),
            ('blue', 'Bleu'),
            ('black', 'Noir'),
        ]
        
        for code, name in colors:
            GlassColor.objects.get_or_create(code=code, defaults={'name': name})

        # Glass Finishes
        finishes = [
            ('polished', 'Poli'),
            ('frosted', 'Dépoli'),
            ('textured', 'Texturé'),
            ('sandblasted', 'Sablé'),
        ]
        
        for code, name in finishes:
            GlassFinish.objects.get_or_create(code=code, defaults={'name': name})

        # Units
        units = [
            ('sqm', 'Mètre carré'),
            ('piece', 'Pièce'),
        ]
        
        for code, name in units:
            Unit.objects.get_or_create(code=code, defaults={'name': name})

        self.stdout.write(
            self.style.SUCCESS('Successfully populated glass data')
        )