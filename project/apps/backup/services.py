# apps/backup/services.py
import io
import os
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
            
            # Validate file first
            if not self.backup_job.import_file:
                raise ValueError("No import file provided")
            
            # Check file extension and format compatibility
            filename = self.backup_job.import_file.name.lower()
            
            if self.backup_job.format == 'json':
                if not filename.endswith('.json'):
                    raise ValueError("JSON format selected but file is not .json")
                return self._import_json_file()
            elif self.backup_job.format == 'csv':
                if filename.endswith('.zip'):
                    return self._import_csv_zip()
                elif filename.endswith('.csv'):
                    return self._import_single_csv()
                else:
                    raise ValueError("CSV format selected but file is not .csv or .zip")
            elif self.backup_job.format == 'excel':
                if not (filename.endswith('.xlsx') or filename.endswith('.xls')):
                    raise ValueError("Excel format selected but file is not .xlsx or .xls")
                return self._import_excel_file()
            else:
                raise ValueError(f"Unsupported format: {self.backup_job.format}")
                
        except Exception as e:
            self.backup_job.status = 'failed'
            self.backup_job.add_log(f"Import error: {str(e)}")
            self.backup_job.save()
            raise
    
    def _import_json_file(self):
        """Import from JSON file"""
        self.backup_job.add_log("Starting JSON import")
        
        try:
            with self.backup_job.import_file.open('r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            self.backup_job.add_log(f"JSON loaded with {len(json_data)} data sections")
            
            imported_count = 0
            
            for resource_name, records in json_data.items():
                self.backup_job.add_log(f"Processing {resource_name} with {len(records) if records else 0} records")
                
                if resource_name in self.resources and records:
                    resource = self.resources[resource_name]
                    
                    # Create dataset from JSON data
                    dataset = Dataset()
                    if records and isinstance(records, list) and len(records) > 0:
                        # Get headers from first record
                        headers = list(records[0].keys())
                        dataset.headers = headers
                        
                        # Add data rows
                        for record in records:
                            row = [record.get(h) for h in headers]
                            dataset.append(row)
                        
                        imported_count += self._import_dataset(resource, dataset, resource_name)
                    else:
                        self.backup_job.add_log(f"No valid records found for {resource_name}")
                else:
                    if resource_name not in self.resources:
                        self.backup_job.add_log(f"Resource {resource_name} not available for import")
                    else:
                        self.backup_job.add_log(f"No records found for {resource_name}")
            
            self._complete_import(imported_count)
            return imported_count
            
        except json.JSONDecodeError as e:
            self.backup_job.add_log(f"JSON parse error: {str(e)}")
            raise ValueError(f"Invalid JSON file: {str(e)}")
        except Exception as e:
            self.backup_job.add_log(f"JSON import error: {str(e)}")
            raise
    
    def _import_csv_zip(self):
        """Import from ZIP archive containing CSV files"""
        self.backup_job.add_log("Starting CSV ZIP import")
        
        imported_count = 0
        
        try:
            with self.backup_job.import_file.open('rb') as f:
                with zipfile.ZipFile(f, 'r') as zip_file:
                    csv_files = [name for name in zip_file.namelist() if name.endswith('.csv')]
                    self.backup_job.add_log(f"Found {len(csv_files)} CSV files in ZIP")
                    
                    for filename in csv_files:
                        # Extract resource name from filename
                        resource_name = os.path.splitext(os.path.basename(filename))[0]
                        
                        self.backup_job.add_log(f"Processing CSV file: {filename} -> {resource_name}")
                        
                        if resource_name in self.resources:
                            resource = self.resources[resource_name]
                            
                            # Read CSV content
                            csv_content = zip_file.read(filename)
                            
                            # Create dataset
                            dataset = Dataset()
                            dataset.load(csv_content.decode('utf-8'), format='csv')
                            
                            if len(dataset) > 0:
                                imported_count += self._import_dataset(resource, dataset, resource_name)
                            else:
                                self.backup_job.add_log(f"No data found in {filename}")
                        else:
                            self.backup_job.add_log(f"Resource {resource_name} not available for import")
            
            self._complete_import(imported_count)
            return imported_count
            
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file")
        except Exception as e:
            self.backup_job.add_log(f"CSV ZIP import error: {str(e)}")
            raise
    
    def _import_single_csv(self):
        """Import from single CSV file"""
        self.backup_job.add_log("Starting single CSV import")
        
        try:
            # For single CSV, we need to determine which resource to use
            # This could be based on filename or user selection
            if len(self.resources) != 1:
                raise ValueError("Single CSV import requires exactly one resource to be selected")
            
            resource_name, resource = next(iter(self.resources.items()))
            
            with self.backup_job.import_file.open('r', encoding='utf-8') as f:
                csv_content = f.read()
            
            dataset = Dataset()
            dataset.load(csv_content, format='csv')
            
            if len(dataset) > 0:
                imported_count = self._import_dataset(resource, dataset, resource_name)
            else:
                imported_count = 0
                self.backup_job.add_log("No data found in CSV file")
            
            self._complete_import(imported_count)
            return imported_count
            
        except Exception as e:
            self.backup_job.add_log(f"Single CSV import error: {str(e)}")
            raise
    
    def _import_excel_file(self):
        """Import from Excel file with multiple worksheets"""
        self.backup_job.add_log("Starting Excel import")
        
        try:
            from tablib import Databook
            
            with self.backup_job.import_file.open('rb') as f:
                content = f.read()
                
            # Load as databook to handle multiple sheets
            databook = Databook()
            databook.load(content, format='xlsx')
            
            self.backup_job.add_log(f"Excel file loaded with {len(databook.sheets())} sheets")
            
            imported_count = 0
            
            for dataset in databook.sheets():
                # Get sheet title/name
                sheet_name = getattr(dataset, 'title', 'Unknown').lower().replace(' ', '_')
                
                self.backup_job.add_log(f"Processing sheet: {sheet_name}")
                
                # Try to match sheet name to resource
                matching_resource = None
                for resource_name, resource in self.resources.items():
                    if resource_name.lower() == sheet_name.lower() or sheet_name in resource_name.lower():
                        matching_resource = (resource_name, resource)
                        break
                
                if matching_resource:
                    resource_name, resource = matching_resource
                    if len(dataset) > 0:
                        imported_count += self._import_dataset(resource, dataset, resource_name)
                    else:
                        self.backup_job.add_log(f"No data found in sheet {sheet_name}")
                else:
                    self.backup_job.add_log(f"No matching resource found for sheet {sheet_name}")
            
            self._complete_import(imported_count)
            return imported_count
            
        except Exception as e:
            self.backup_job.add_log(f"Excel import error: {str(e)}")
            raise
    
    def _import_dataset(self, resource, dataset, resource_name):
        """Import a single dataset using resource"""
        try:
            if not dataset or len(dataset) == 0:
                self.backup_job.add_log(f"No data to import for {resource_name}")
                return 0
            
            self.backup_job.add_log(f"Starting import of {len(dataset)} records for {resource_name}")
            
            # Perform dry run first
            dry_result = resource.import_data(dataset, dry_run=True)
            
            if dry_result.has_errors():
                self.backup_job.add_log(f"Validation errors found for {resource_name}:")
                # Fix: Properly handle row_errors() return format
                for row_num, row_errors in dry_result.row_errors():
                    for error in row_errors:
                        self.backup_job.add_log(f"  Row {row_num + 1}: {error.error}")
                        self.backup_job.error_count += 1
                
                # Also check for non-row errors
                if hasattr(dry_result, 'base_errors') and dry_result.base_errors:
                    for error in dry_result.base_errors:
                        self.backup_job.add_log(f"  General error: {error.error}")
                        self.backup_job.error_count += 1
                
                # Don't proceed with import if there are validation errors
                self.backup_job.add_log(f"Skipping import for {resource_name} due to validation errors")
                return 0
            
            # Perform actual import
            self.backup_job.add_log(f"Validation passed, proceeding with import for {resource_name}")
            result = resource.import_data(dataset, dry_run=False)
            
            # Count successful imports
            successful_imports = 0
            if hasattr(result, 'rows'):
                for row in result.rows:
                    if not row.errors:
                        successful_imports += 1
                    else:
                        for error in row.errors:
                            self.backup_job.add_log(f"Import error: {error.error}")
                            self.backup_job.error_count += 1
            else:
                # Fallback: assume all rows imported successfully if no errors
                successful_imports = len(dataset)
            
            self.backup_job.add_log(f"Successfully imported {successful_imports} {resource_name} records")
            return successful_imports
            
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
        self.backup_job.add_log(f"Import completed. Total records imported: {imported_count}")
    
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
            if not self.backup_job.import_file:
                return False, "No import file provided"
            
            filename = self.backup_job.import_file.name.lower()
            
            if self.backup_job.format == 'json':
                if not filename.endswith('.json'):
                    return False, "JSON format selected but file is not .json"
                return self._validate_json_file()
            elif self.backup_job.format == 'csv':
                if filename.endswith('.zip'):
                    return self._validate_csv_zip()
                elif filename.endswith('.csv'):
                    return self._validate_single_csv()
                else:
                    return False, "CSV format selected but file is not .csv or .zip"
            elif self.backup_job.format == 'excel':
                if not (filename.endswith('.xlsx') or filename.endswith('.xls')):
                    return False, "Excel format selected but file is not .xlsx or .xls"
                return self._validate_excel_file()
            else:
                return False, f"Unsupported format: {self.backup_job.format}"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_json_file(self):
        """Validate JSON file structure"""
        try:
            with self.backup_job.import_file.open('r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if not isinstance(json_data, dict):
                return False, "JSON file must contain an object with data sections"
            
            return True, f"Valid JSON file with {len(json_data)} data sections"
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
        except Exception as e:
            return False, f"JSON validation error: {str(e)}"
    
    def _validate_csv_zip(self):
        """Validate CSV ZIP archive"""
        try:
            with self.backup_job.import_file.open('rb') as f:
                with zipfile.ZipFile(f, 'r') as zip_file:
                    csv_files = [name for name in zip_file.namelist() if name.endswith('.csv')]
                    
                    if not csv_files:
                        return False, "No CSV files found in ZIP archive"
                    
                    # Test first CSV file
                    first_csv = zip_file.read(csv_files[0])
                    dataset = Dataset()
                    dataset.load(first_csv.decode('utf-8'), format='csv')
                    
                    return True, f"Valid CSV ZIP archive with {len(csv_files)} files"
                    
        except zipfile.BadZipFile:
            return False, "Invalid ZIP file"
        except Exception as e:
            return False, f"CSV ZIP validation error: {str(e)}"
    
    def _validate_single_csv(self):
        """Validate single CSV file"""
        try:
            with self.backup_job.import_file.open('r', encoding='utf-8') as f:
                content = f.read()
            
            dataset = Dataset()
            dataset.load(content, format='csv')
            
            return True, f"Valid CSV file with {len(dataset)} rows"
            
        except Exception as e:
            return False, f"CSV validation error: {str(e)}"
    
    def _validate_excel_file(self):
        """Validate Excel file"""
        try:
            from tablib import Databook
            
            with self.backup_job.import_file.open('rb') as f:
                content = f.read()
            
            databook = Databook()
            databook.load(content, format='xlsx')
            
            return True, f"Valid Excel file with {len(databook.sheets())} sheets"
            
        except Exception as e:
            return False, f"Excel validation error: {str(e)}"