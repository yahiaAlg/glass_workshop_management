# apps/backup/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import View
import os
import threading
from .models import BackupJob
from .services import BackupService
from .forms import ExportForm, ImportForm

@login_required
def backup_list(request):
    """List all backup jobs"""
    jobs = BackupJob.objects.filter(created_by=request.user)
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        jobs = jobs.filter(
            Q(job_type__icontains=search) |
            Q(format__icontains=search) |
            Q(status__icontains=search)
        )
    
    # Filter by job type
    job_type = request.GET.get('job_type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        jobs = jobs.filter(status=status)
    
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    
    context = {
        'jobs': jobs,
        'search': search,
        'job_type': job_type,
        'status': status,
        'job_types': BackupJob.JOB_TYPES,
        'statuses': BackupJob.STATUS_CHOICES,
    }
    
    return render(request, 'backup/list.html', context)

# Replace the export_data view in views.py with this fixed version

@login_required
def export_data(request):
    """Export data form and processing"""
    if request.method == 'POST':
        form = ExportForm(request.POST)
        if form.is_valid():
            # Debug: Print form data
            print("Form cleaned_data:", form.cleaned_data)
            
            # Create backup job using form.save() to handle field conversion
            job = form.save(commit=False)
            job.job_type = 'export'
            job.created_by = request.user
            job.save()
            
            # Debug: Print job fields after creation
            job.add_log(f"Job created with options:")
            job.add_log(f"- Customers: {job.include_customers}")
            job.add_log(f"- Products: {job.include_products}")
            job.add_log(f"- Orders: {job.include_orders}")
            job.add_log(f"- Invoices: {job.include_invoices}")
            job.add_log(f"- Suppliers: {job.include_suppliers}")
            job.add_log(f"- Company: {job.include_company}")
            if hasattr(job, 'include_audit'):
                job.add_log(f"- Audit: {job.include_audit}")
            
            # Start export in background
            def run_export():
                try:
                    service = BackupService(job)
                    service.export_data()
                except Exception as e:
                    job.add_log(f"Export thread error: {str(e)}")
                    job.status = 'failed'
                    job.save()
            
            thread = threading.Thread(target=run_export)
            thread.daemon = True
            thread.start()
            
            messages.success(request, f'Export lancé avec succès. Tâche #{job.id}')
            return redirect('backup:detail', pk=job.id)
        else:
            # Debug: Print form errors
            print("Form errors:", form.errors)
    else:
        form = ExportForm()
    
    return render(request, 'backup/export.html', {'form': form})

@login_required
def import_data(request):
    """Import data form and processing"""
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            # Create backup job
            job = BackupJob.objects.create(
                job_type='import',
                created_by=request.user,
                import_file=form.cleaned_data['import_file'],
                format=form.cleaned_data['format']
            )
            
            # Start import in background
            def run_import():
                service = BackupService(job)
                service.import_data()
            
            thread = threading.Thread(target=run_import)
            thread.daemon = True
            thread.start()
            
            messages.success(request, f'Import lancé avec succès. Tâche #{job.id}')
            return redirect('backup:detail', pk=job.id)
    else:
        form = ImportForm()
    
    return render(request, 'backup/import.html', {'form': form})

@login_required
def backup_detail(request, pk):
    """View backup job details"""
    job = get_object_or_404(BackupJob, pk=pk, created_by=request.user)
    
    context = {
        'job': job,
        'progress': job.get_progress_percentage(),
    }
    
    return render(request, 'backup/detail.html', context)

@login_required
def backup_status(request, pk):
    """AJAX endpoint for backup status"""
    job = get_object_or_404(BackupJob, pk=pk, created_by=request.user)
    
    data = {
        'status': job.status,
        'progress': job.get_progress_percentage(),
        'processed_records': job.processed_records,
        'total_records': job.total_records,
        'error_count': job.error_count,
        'log_messages': job.log_messages,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
    }
    
    return JsonResponse(data)

@login_required
def download_backup(request, pk):
    """Download backup file"""
    job = get_object_or_404(BackupJob, pk=pk, created_by=request.user)
    
    if job.job_type != 'export' or job.status != 'completed':
        raise Http404("Fichier non disponible")
    
    if not job.export_file:
        raise Http404("Fichier non trouvé")
    
    response = HttpResponse(
        job.export_file.read(),
        content_type='application/octet-stream'
    )
    
    filename = os.path.basename(job.export_file.name)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
def delete_backup(request, pk):
    """Delete backup job"""
    job = get_object_or_404(BackupJob, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        # Delete associated files
        if job.export_file:
            job.export_file.delete()
        if job.import_file:
            job.import_file.delete()
        
        job.delete()
        messages.success(request, 'Tâche de sauvegarde supprimée avec succès.')
        return redirect('backup:list')
    
    return render(request, 'backup/delete.html', {'job': job})

class BackupDashboardView(View):
    """Backup dashboard with statistics"""
    
    @method_decorator(login_required)
    def get(self, request):
        jobs = BackupJob.objects.filter(created_by=request.user)
        
        stats = {
            'total_jobs': jobs.count(),
            'completed_jobs': jobs.filter(status='completed').count(),
            'failed_jobs': jobs.filter(status='failed').count(),
            'processing_jobs': jobs.filter(status='processing').count(),
            'export_jobs': jobs.filter(job_type='export').count(),
            'import_jobs': jobs.filter(job_type='import').count(),
        }
        
        recent_jobs = jobs.order_by('-created_at')[:5]
        
        context = {
            'stats': stats,
            'recent_jobs': recent_jobs,
        }
        
        return render(request, 'backup/dashboard.html', context)