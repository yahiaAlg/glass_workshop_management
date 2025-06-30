# apps/backup/services.py
import io
import zipfile
import json
from datetime import datetime
from django.core.files.base import ContentFile
from import_export.formats import base_formats
from tablib import Dataset

class BackupService:
    def __init__(self, backup_job):
        self.backup_job = backup_job
        self.resources = self._get_resources()
        self.format_registry = {
            'json': base_formats.JSON,
            'excel': base_formats.XLSX,
            'csv': base_formats.CSV
        }
    
    def _get_resources(self):
        """Get import-export resources for selected models"""
        resources = {}
        
        # Debug: Log which options are selected
        selected_options = []
        for attr in ['include_company', 'include_customers', 'include_products', 'include_suppliers', 'include_orders', 'include_invoices']:
            if getattr(self.backup_job, attr, False):
                selected_options.append(attr)
        
        self.backup_job.add_log(f"Selected options: {selected_options}")
        
        # Map backup job attributes to resources
        resource_mapping = {
            'include_company': ('apps.company.resources', 'CompanyResource', 'company'),
            'include_customers': ('apps.customers.resources', 'CustomerResource', 'customers'),
            'include_products': ('apps.inventory.resources', 'GlassProductResource', 'products'),
            'include_suppliers': ('apps.suppliers.resources', 'SupplierResource', 'suppliers'),
            'include_orders': ('apps.orders.resources', ['OrderResource', 'OrderItemResource'], ['orders', 'order_items']),
            'include_invoices': ('apps.invoices.resources', 
                               ['InvoiceResource', 'InvoiceItemResource', 'InvoiceServiceResource', 'PaymentResource'],
                               ['invoices', 'invoice_items', 'invoice_services', 'payments']),
        }
        
        # Add audit resources if available
        if hasattr(self.backup_job, 'include_audit') and self.backup_job.include_audit:
            resource_mapping['include_audit'] = (
                'apps.audit.resources',
                ['ExpenseCategoryResource', 'RevenueCategoryResource', 'AdditionalExpenseResource', 'AdditionalRevenueResource'],
                ['expense_categories', 'revenue_categories', 'additional_expenses', 'additional_revenues']
            )
        
        for attr, (module_path, resource_classes, keys) in resource_mapping.items():
            if getattr(self.backup_job, attr, False):
                self.backup_job.add_log(f"Attempting to load {attr} from {module_path}")
                try:
                    module = __import__(module_path, fromlist=[''])
                    self.backup_job.add_log(f"Successfully imported module {module_path}")
                    
                    if isinstance(resource_classes, list):
                        for resource_class, key in zip(resource_classes, keys):
                            if hasattr(module, resource_class):
                                resources[key] = getattr(module, resource_class)()
                                self.backup_job.add_log(f"Loaded resource {resource_class} as {key}")
                            else:
                                self.backup_job.add_log(f"Resource class {resource_class} not found in module")
                    else:
                        if hasattr(module, resource_classes):
                            resources[keys] = getattr(module, resource_classes)()
                            self.backup_job.add_log(f"Loaded resource {resource_classes} as {keys}")
                        else:
                            self.backup_job.add_log(f"Resource class {resource_classes} not found in module")
                            
                except ImportError as e:
                    self.backup_job.add_log(f"Resource import error for {attr}: {str(e)}")
                except Exception as e:
                    self.backup_job.add_log(f"Unexpected error loading {attr}: {str(e)}")
        
        self.backup_job.add_log(f"Loaded {len(resources)} resources: {list(resources.keys())}")
        return resources
    
    def export_data(self):
        """Export data using django-import-export built-in methods"""
        try:
            self.backup_job.status = 'processing'
            self.backup_job.save()
            
            # Debug logging
            self.backup_job.add_log(f"Starting export with {len(self.resources)} resources")
            self.backup_job.add_log(f"Export settings - customers: {self.backup_job.include_customers}, products: {self.backup_job.include_products}, orders: {self.backup_job.include_orders}")
            
            if not self.resources:
                raise ValueError("No resources loaded for export. Check resource loading and selection.")
            
            format_class = self.format_registry.get(self.backup_job.format)
            if not format_class:
                raise ValueError(f"Unsupported format: {self.backup_job.format}")
            
            format_instance = format_class()
            
            if self.backup_job.format == 'csv':
                return self._export_csv_archive(format_instance)
            elif self.backup_job.format == 'excel':
                return self._export_excel_workbook(format_instance)
            else:  # JSON
                return self._export_json_single(format_instance)
                
        except Exception as e:
            self.backup_job.status = 'failed'
            self.backup_job.add_log(f"Export error: {str(e)}")
            self.backup_job.save()
            raise
    
    def _export_excel_workbook(self, format_instance):
        """Export using XLSX format with multiple worksheets"""
        datasets = {}
        
        # Collect all datasets
        for name, resource in self.resources.items():
            try:
                queryset = self._get_filtered_queryset(resource)
                if queryset is not None and queryset.exists():
                    dataset = resource.export(queryset)
                    if dataset and len(dataset) > 0:
                        datasets[name] = dataset
                        self.backup_job.processed_records += len(dataset)
                        self.backup_job.add_log(f"Prepared {len(dataset)} {name} records")
                else:
                    self.backup_job.add_log(f"No data found for {name}")
            except Exception as e:
                self.backup_job.add_log(f"Error preparing {name}: {str(e)}")
                continue
        
        if not datasets:
            raise ValueError("No data available for export")
        
        # Use tablib's built-in Excel export with multiple sheets
        from tablib import Databook
        
        databook = Databook()
        for name, dataset in datasets.items():
            # Ensure dataset has a title for the sheet name
            dataset.title = name.replace('_', ' ').title()[:31]  # Excel sheet name limit
            databook.add_sheet(dataset)
        
        # Export using format instance
        content = databook.export('xlsx')
        
        # Save file
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.backup_job.export_file.save(filename, ContentFile(content))
        
        self._complete_export()
        return self.backup_job.export_file
    
    def _export_json_single(self, format_instance):
        """Export using JSON format - single file with all data"""
        combined_data = {}
        
        for name, resource in self.resources.items():
            try:
                queryset = self._get_filtered_queryset(resource)
                if queryset is not None and queryset.exists():
                    dataset = resource.export(queryset)
                    if dataset and len(dataset) > 0:
                        # Convert dataset to list of dictionaries for JSON serialization
                        data_list = []
                        headers = dataset.headers
                        for row in dataset:
                            row_dict = {}
                            for i, header in enumerate(headers):
                                # Get value safely, handle index out of range
                                value = row[i] if i < len(row) else None
                                row_dict[header] = value
                            data_list.append(row_dict)
                        
                        combined_data[name] = data_list
                        self.backup_job.processed_records += len(dataset)
                        self.backup_job.add_log(f"Exported {len(dataset)} {name} records")
                else:
                    self.backup_job.add_log(f"No data found for {name}")
            except Exception as e:
                self.backup_job.add_log(f"Error exporting {name}: {str(e)}")
                continue
        
        if not combined_data:
            raise ValueError("No data available for export")
        
        # Create JSON content directly
        json_content = json.dumps(combined_data, indent=2, default=str)
        
        # Save file
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.backup_job.export_file.save(filename, ContentFile(json_content.encode('utf-8')))
        
        self._complete_export()
        return self.backup_job.export_file
    
    def _export_csv_archive(self, format_instance):
        """Export using CSV format - ZIP archive with multiple CSV files"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for name, resource in self.resources.items():
                try:
                    queryset = self._get_filtered_queryset(resource)
                    if queryset is not None and queryset.exists():
                        dataset = resource.export(queryset)
                        if dataset and len(dataset) > 0:
                            # Use format instance to export CSV
                            csv_content = format_instance.export_data(dataset)
                            zip_file.writestr(f"{name}.csv", csv_content)
                            
                            self.backup_job.processed_records += len(dataset)
                            self.backup_job.add_log(f"Exported {len(dataset)} {name} records")
                    else:
                        self.backup_job.add_log(f"No data found for {name}")
                except Exception as e:
                    self.backup_job.add_log(f"Error exporting {name}: {str(e)}")
                    continue
        
        if self.backup_job.processed_records == 0:
            raise ValueError("No data available for export")
        
        zip_buffer.seek(0)
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        self.backup_job.export_file.save(filename, ContentFile(zip_buffer.getvalue()))
        
        self._complete_export()
        return self.backup_job.export_file
    
    def _complete_export(self):
        """Mark export as completed"""
        self.backup_job.status = 'completed'
        self.backup_job.completed_at = datetime.now()
        self.backup_job.save()
    
    def import_data(self):
        """Import data using django-import-export built-in methods"""
        try:
            self.backup_job.status = 'processing'
            self.backup_job.save()
            
            format_class = self.format_registry.get(self.backup_job.format)
            if not format_class:
                raise ValueError(f"Unsupported format: {self.backup_job.format}")
            
            format_instance = format_class()
            
            with self.backup_job.import_file.open('rb') as f:
                if self.backup_job.format == 'csv' and self.backup_job.import_file.name.endswith('.zip'):
                    return self._import_csv_archive(f, format_instance)
                elif self.backup_job.format == 'excel':
                    return self._import_excel_workbook(f, format_instance)
                else:  # JSON
                    return self._import_json_single(f, format_instance)
                    
        except Exception as e:
            self.backup_job.status = 'failed'
            self.backup_job.add_log(f"Import error: {str(e)}")
            self.backup_job.save()
            raise
    
    def _import_excel_workbook(self, file_obj, format_instance):
        """Import from Excel workbook using tablib"""
        from tablib import Databook
        
        # Load the databook using format instance
        content = file_obj.read()
        databook = Databook().load(content, format='xlsx')
        
        imported_count = 0
        
        for dataset in databook.sheets():
            # Match sheet title to resource name
            sheet_title = getattr(dataset, 'title', '').lower().replace(' ', '_')
            
            if sheet_title in self.resources:
                resource = self.resources[sheet_title]
                imported_count += self._import_dataset(resource, dataset, sheet_title)
        
        self._complete_import(imported_count)
        return imported_count
    
    def _import_json_single(self, file_obj, format_instance):
        """Import from JSON file"""
        content = file_obj.read()
        
        try:
            # Parse JSON directly
            json_data = json.loads(content.decode('utf-8'))
            
            imported_count = 0
            
            for resource_name, records in json_data.items():
                if resource_name in self.resources and records:
                    resource = self.resources[resource_name]
                    
                    # Create new dataset for this resource
                    resource_dataset = Dataset()
                    if records and isinstance(records, list) and len(records) > 0:
                        # Get headers from first record
                        headers = list(records[0].keys())
                        resource_dataset.headers = headers
                        
                        # Add data rows
                        for record in records:
                            row = [record.get(h, '') for h in headers]
                            resource_dataset.append(row)
                    
                    imported_count += self._import_dataset(resource, resource_dataset, resource_name)
        
        except json.JSONDecodeError as e:
            self.backup_job.add_log(f"JSON parse error: {str(e)}")
            imported_count = 0
        
        self._complete_import(imported_count)
        return imported_count
    
    def _import_csv_archive(self, file_obj, format_instance):
        """Import from ZIP archive with CSV files"""
        imported_count = 0
        
        with zipfile.ZipFile(file_obj, 'r') as zip_file:
            for filename in zip_file.namelist():
                if filename.endswith('.csv'):
                    resource_name = filename[:-4]  # Remove .csv extension
                    
                    if resource_name in self.resources:
                        resource = self.resources[resource_name]
                        
                        # Read and load CSV content
                        csv_content = zip_file.read(filename)
                        dataset = Dataset()
                        dataset.load(csv_content, format='csv')
                        
                        imported_count += self._import_dataset(resource, dataset, resource_name)
        
        self._complete_import(imported_count)
        return imported_count
    
    def _import_dataset(self, resource, dataset, resource_name):
        """Import a single dataset using resource"""
        try:
            if not dataset or len(dataset) == 0:
                return 0
            
            # Perform dry run first
            dry_result = resource.import_data(dataset, dry_run=True)
            
            if dry_result.has_errors():
                for error in dry_result.row_errors():
                    self.backup_job.add_log(f"Validation error in {resource_name}: {error}")
                    self.backup_job.error_count += 1
                return 0
            
            # Perform actual import
            result = resource.import_data(dataset, dry_run=False)
            
            imported_records = len([row for row in result.rows if not row.errors])
            self.backup_job.add_log(f"Imported {imported_records} {resource_name} records")
            
            # Log any import errors
            if result.has_errors():
                for error in result.row_errors():
                    self.backup_job.add_log(f"Import error in {resource_name}: {error}")
                    self.backup_job.error_count += 1
            
            return imported_records
            
        except Exception as e:
            self.backup_job.add_log(f"Error importing {resource_name}: {str(e)}")
            self.backup_job.error_count += 1
            return 0
    
    def _complete_import(self, imported_count):
        """Mark import as completed"""
        self.backup_job.processed_records = imported_count
        self.backup_job.status = 'completed'
        self.backup_job.completed_at = datetime.now()
        self.backup_job.save()
    
    def _get_filtered_queryset(self, resource):
        """Apply date filters to resource queryset"""
        try:
            if not hasattr(resource._meta, 'model') or not resource._meta.model:
                self.backup_job.add_log(f"Resource {resource.__class__.__name__} has no model")
                return None
                
            queryset = resource._meta.model.objects.all()
            total_count = queryset.count()
            self.backup_job.add_log(f"Found {total_count} total records for {resource.__class__.__name__}")
            
            # Apply date filtering using resource's date_field
            date_field = getattr(resource._meta, 'date_field', 'created_at')
            
            # Check if date field exists on model
            if hasattr(queryset.model, date_field):
                if self.backup_job.date_from:
                    queryset = queryset.filter(**{f"{date_field}__gte": self.backup_job.date_from})
                    self.backup_job.add_log(f"Applied date_from filter: {self.backup_job.date_from}")
                if self.backup_job.date_to:
                    queryset = queryset.filter(**{f"{date_field}__lte": self.backup_job.date_to})
                    self.backup_job.add_log(f"Applied date_to filter: {self.backup_job.date_to}")
                    
                filtered_count = queryset.count()
                self.backup_job.add_log(f"After filtering: {filtered_count} records for {resource.__class__.__name__}")
            else:
                self.backup_job.add_log(f"Date field '{date_field}' not found on {queryset.model.__name__}, skipping date filters")
            
            return queryset
            
        except Exception as e:
            self.backup_job.add_log(f"Error filtering queryset for {resource.__class__.__name__}: {str(e)}")
            return None
    
    def validate_import_file(self):
        """Validate import file format and structure"""
        try:
            format_class = self.format_registry.get(self.backup_job.format)
            if not format_class:
                return False, f"Unsupported format: {self.backup_job.format}"
            
            format_instance = format_class()
            
            with self.backup_job.import_file.open('rb') as f:
                if self.backup_job.format == 'csv' and self.backup_job.import_file.name.endswith('.zip'):
                    return self._validate_csv_archive(f)
                else:
                    content = f.read()
                    try:
                        # Test if format can read the content
                        dataset = Dataset()
                        dataset.load(content, format=self.backup_job.format)
                        return True, "File format is valid"
                    except Exception as e:
                        return False, f"Invalid file format: {str(e)}"
                        
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_csv_archive(self, file_obj):
        """Validate CSV archive structure"""
        try:
            with zipfile.ZipFile(file_obj, 'r') as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                if not csv_files:
                    return False, "No CSV files found in archive"
                
                # Test read first CSV file
                first_csv = zip_file.read(csv_files[0])
                dataset = Dataset()
                dataset.load(first_csv, format='csv')
                
                return True, f"Valid CSV archive with {len(csv_files)} files"
                
        except Exception as e:
            return False, f"Invalid CSV archive: {str(e)}"