# apps/backup/services.py
import json
import csv
import io
from datetime import datetime
from decimal import Decimal
from django.core.serializers import serialize
from django.apps import apps
from django.db import transaction
from django.core.files.base import ContentFile
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

class BackupService:
    def __init__(self, backup_job):
        self.backup_job = backup_job
        self.models_to_process = self._get_models_to_process()
    
    def _get_models_to_process(self):
        """Get list of models to process based on job configuration"""
        models = {}
        
        if self.backup_job.include_company:
            models['company'] = apps.get_model('company', 'Company')
            
        if self.backup_job.include_customers:
            models['customers'] = apps.get_model('customers', 'Customer')
            
        if self.backup_job.include_products:
            models['products'] = apps.get_model('inventory', 'GlassProduct')
            
        if self.backup_job.include_suppliers:
            models['suppliers'] = apps.get_model('suppliers', 'Supplier')
            
        if self.backup_job.include_orders:
            models['orders'] = apps.get_model('orders', 'Order')
            models['order_items'] = apps.get_model('orders', 'OrderItem')
            
        if self.backup_job.include_invoices:
            models['invoices'] = apps.get_model('invoices', 'Invoice')
            models['invoice_items'] = apps.get_model('invoices', 'InvoiceItem')
            models['invoice_services'] = apps.get_model('invoices', 'InvoiceService')
            models['payments'] = apps.get_model('invoices', 'Payment')
        
        return models
    
    def export_data(self):
        """Export data based on format"""
        try:
            self.backup_job.status = 'processing'
            self.backup_job.save()
            
            if self.backup_job.format == 'json':
                return self._export_json()
            elif self.backup_job.format == 'excel':
                return self._export_excel()
            elif self.backup_job.format == 'csv':
                return self._export_csv()
                
        except Exception as e:
            self.backup_job.status = 'failed'
            self.backup_job.add_log(f"Erreur lors de l'export: {str(e)}")
            raise
    
    def _export_json(self):
        """Export to JSON format"""
        data = {}
        total_records = 0
        
        # Calculate total records
        for name, model in self.models_to_process.items():
            queryset = self._get_filtered_queryset(model)
            total_records += queryset.count()
        
        self.backup_job.total_records = total_records
        self.backup_job.save()
        
        # Export each model
        for name, model in self.models_to_process.items():
            queryset = self._get_filtered_queryset(model)
            serialized_data = serialize('json', queryset)
            data[name] = json.loads(serialized_data)
            
            self.backup_job.processed_records += queryset.count()
            self.backup_job.add_log(f"Exporté {queryset.count()} enregistrements de {name}")
        
        # Add metadata
        data['_metadata'] = {
            'export_date': datetime.now().isoformat(),
            'version': '1.0',
            'total_records': total_records
        }
        
        # Save to file
        json_content = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        self.backup_job.export_file.save(
            filename,
            ContentFile(json_content.encode('utf-8'))
        )
        
        self.backup_job.status = 'completed'
        self.backup_job.completed_at = datetime.now()
        self.backup_job.save()
        
        return self.backup_job.export_file
    
    def _export_excel(self):
        """Export to Excel format"""
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        total_records = sum(self._get_filtered_queryset(model).count() 
                          for model in self.models_to_process.values())
        self.backup_job.total_records = total_records
        self.backup_job.save()
        
        for name, model in self.models_to_process.items():
            ws = wb.create_sheet(title=name.capitalize())
            queryset = self._get_filtered_queryset(model)
            
            if queryset.exists():
                # Get field names
                fields = [f.name for f in model._meta.fields]
                
                # Header row
                for col, field in enumerate(fields, 1):
                    cell = ws.cell(row=1, column=col, value=field.replace('_', ' ').title())
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                
                # Data rows
                for row_idx, obj in enumerate(queryset, 2):
                    for col_idx, field in enumerate(fields, 1):
                        value = getattr(obj, field)
                        if isinstance(value, Decimal):
                            value = float(value)
                        elif hasattr(value, 'strftime'):
                            value = value.strftime('%Y-%m-%d %H:%M:%S') if hasattr(value, 'hour') else value.strftime('%Y-%m-%d')
                        ws.cell(row=row_idx, column=col_idx, value=str(value) if value is not None else '')
                
                self.backup_job.processed_records += queryset.count()
                self.backup_job.add_log(f"Exporté {queryset.count()} enregistrements de {name}")
        
        # Save to file
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.backup_job.export_file.save(
            filename,
            ContentFile(buffer.getvalue())
        )
        
        self.backup_job.status = 'completed'
        self.backup_job.completed_at = datetime.now()
        self.backup_job.save()
        
        return self.backup_job.export_file
    
    def _export_csv(self):
        """Export to CSV format (ZIP with multiple CSV files)"""
        import zipfile
        
        zip_buffer = io.BytesIO()
        
        total_records = sum(self._get_filtered_queryset(model).count() 
                          for model in self.models_to_process.values())
        self.backup_job.total_records = total_records
        self.backup_job.save()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for name, model in self.models_to_process.items():
                queryset = self._get_filtered_queryset(model)
                
                if queryset.exists():
                    csv_buffer = io.StringIO()
                    writer = csv.writer(csv_buffer)
                    
                    # Header
                    fields = [f.name for f in model._meta.fields]
                    writer.writerow(fields)
                    
                    # Data
                    for obj in queryset:
                        row = []
                        for field in fields:
                            value = getattr(obj, field)
                            if isinstance(value, Decimal):
                                value = float(value)
                            elif hasattr(value, 'strftime'):
                                value = value.strftime('%Y-%m-%d %H:%M:%S') if hasattr(value, 'hour') else value.strftime('%Y-%m-%d')
                            row.append(str(value) if value is not None else '')
                        writer.writerow(row)
                    
                    zip_file.writestr(f"{name}.csv", csv_buffer.getvalue())
                    
                    self.backup_job.processed_records += queryset.count()
                    self.backup_job.add_log(f"Exporté {queryset.count()} enregistrements de {name}")
        
        zip_buffer.seek(0)
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        self.backup_job.export_file.save(
            filename,
            ContentFile(zip_buffer.getvalue())
        )
        
        self.backup_job.status = 'completed'
        self.backup_job.completed_at = datetime.now()
        self.backup_job.save()
        
        return self.backup_job.export_file
    
    def _get_filtered_queryset(self, model):
        """Get filtered queryset based on date range"""
        queryset = model.objects.all()
        
        # Apply date filters if available
        if hasattr(model, 'created_at') and (self.backup_job.date_from or self.backup_job.date_to):
            if self.backup_job.date_from:
                queryset = queryset.filter(created_at__gte=self.backup_job.date_from)
            if self.backup_job.date_to:
                queryset = queryset.filter(created_at__lte=self.backup_job.date_to)
        
        return queryset
    
    def import_data(self):
        """Import data from file"""
        try:
            self.backup_job.status = 'processing'
            self.backup_job.save()
            
            if self.backup_job.format == 'json':
                return self._import_json()
            elif self.backup_job.format == 'excel':
                return self._import_excel()
            elif self.backup_job.format == 'csv':
                return self._import_csv()
                
        except Exception as e:
            self.backup_job.status = 'failed'
            self.backup_job.add_log(f"Erreur lors de l'import: {str(e)}")
            raise
    
    def _import_json(self):
        """Import from JSON format"""
        with self.backup_job.import_file.open('r') as f:
            data = json.load(f)
        
        imported_count = 0
        
        with transaction.atomic():
            for model_name, records in data.items():
                if model_name.startswith('_'):  # Skip metadata
                    continue
                    
                if model_name not in self.models_to_process:
                    continue
                
                model = self.models_to_process[model_name]
                
                for record_data in records:
                    try:
                        # Extract fields from serialized format
                        fields = record_data['fields']
                        pk = record_data['pk']
                        
                        # Create or update object
                        obj, created = model.objects.update_or_create(
                            pk=pk,
                            defaults=fields
                        )
                        
                        imported_count += 1
                        self.backup_job.processed_records += 1
                        
                    except Exception as e:
                        self.backup_job.error_count += 1
                        self.backup_job.add_log(f"Erreur import {model_name} ID {pk}: {str(e)}")
                
                self.backup_job.add_log(f"Importé {len(records)} enregistrements de {model_name}")
        
        self.backup_job.status = 'completed'
        self.backup_job.completed_at = datetime.now()
        self.backup_job.save()
        
        return imported_count