# management/commands/clean_backup.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
import json
from datetime import datetime

class Command(BaseCommand):
    help = 'Clean and recreate backup files without problematic foreign keys'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-file',
            type=str,
            help='Path to backup file to clean',
        )
        parser.add_argument(
            '--create-clean',
            action='store_true',
            help='Create a new clean backup',
        )

    def handle(self, *args, **options):
        if options['backup_file']:
            self.clean_backup_file(options['backup_file'])
        
        if options['create_clean']:
            self.create_clean_backup()

    def clean_backup_file(self, file_path):
        """Remove problematic entries from existing backup file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Remove problematic models
            problematic_models = [
                'contenttypes.contenttype',
                'auth.permission',
                'auth.group_permissions',
                'sessions.session',
                'admin.logentry',
            ]
            
            cleaned_data = []
            removed_count = 0
            
            for item in data:
                if item.get('model') not in problematic_models:
                    cleaned_data.append(item)
                else:
                    removed_count += 1
            
            # Create cleaned backup
            base_name = os.path.splitext(file_path)[0]
            cleaned_path = f"{base_name}_cleaned.json"
            
            with open(cleaned_path, 'w') as f:
                json.dump(cleaned_data, f, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Cleaned backup created: {cleaned_path} '
                    f'(removed {removed_count} problematic entries)'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error cleaning backup: {e}')
            )

    def create_clean_backup(self):
        """Create a new clean backup excluding problematic models"""
        try:
            backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"clean_backup_{timestamp}.json"
            file_path = os.path.join(backup_dir, filename)
            
            exclude = [
                'contenttypes',
                'auth.permission',
                'auth.group_permissions',
                'auth.user_groups',
                'auth.user_user_permissions',
                'sessions',
                'admin.logentry',
            ]
            
            call_command('dumpdata',
                       exclude=exclude,
                       output=file_path,
                       indent=2,
                       natural_foreign=True,
                       natural_primary=True)
            
            self.stdout.write(
                self.style.SUCCESS(f'Clean backup created: {file_path}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating clean backup: {e}')
            )