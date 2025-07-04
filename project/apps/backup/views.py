from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.core.management import call_command
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db import transaction
from django.contrib.auth import get_user_model
import os
import json
import tempfile
from datetime import datetime
from .models import BackupRecord, RestoreRecord
from .forms import BackupForm, RestoreForm, BackupSelectForm

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    recent_backups = BackupRecord.objects.filter(created_by=request.user)[:5]
    recent_restores = RestoreRecord.objects.filter(restored_by=request.user)[:5]
    
    context = {
        'recent_backups': recent_backups,
        'recent_restores': recent_restores,
        'total_backups': BackupRecord.objects.count(),
        'successful_backups': BackupRecord.objects.filter(status='completed').count(),
    }
    return render(request, 'backup/dashboard.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class BackupListView(ListView):
    model = BackupRecord
    template_name = 'backup/backup_list.html'
    context_object_name = 'backups'
    paginate_by = 10
    
    def get_queryset(self):
        return BackupRecord.objects.all().order_by('-created_at')

@login_required
@user_passes_test(is_admin)
def create_backup(request):
    if request.method == 'POST':
        form = BackupForm(request.POST)
        if form.is_valid():
            backup = form.save(commit=False)
            backup.created_by = request.user
            backup.status = 'processing'
            backup.save()
            
            # Create backup file
            try:
                backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
                os.makedirs(backup_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{backup.name}_{timestamp}.json"
                file_path = os.path.join(backup_dir, filename)
                
                # Enhanced exclusion list for better compatibility
                base_exclude = [
                    'contenttypes',
                    'auth.permission',
                    'auth.group_permissions',
                    'sessions',
                    'admin.logentry',
                ]
                
                # Determine what to backup
                if backup.backup_type == 'full':
                    exclude = base_exclude if form.cleaned_data.get('exclude_sensitive') else ['contenttypes', 'auth.permission']
                    
                    # Create a StringIO buffer to capture dumpdata output
                    from io import StringIO
                    output_buffer = StringIO()
                    
                    # Call dumpdata with string buffer
                    call_command('dumpdata', 
                               exclude=exclude,
                               stdout=output_buffer,
                               indent=2,
                               natural_foreign=True,
                               natural_primary=True)
                    
                    # Get the JSON string and write it with proper UTF-8 encoding
                    json_data = output_buffer.getvalue()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(json_data)
                    
                else:
                    # Partial backup
                    apps = form.cleaned_data.get('apps_to_backup', [])
                    if apps:
                        from io import StringIO
                        output_buffer = StringIO()
                        
                        call_command('dumpdata',
                                   *apps,
                                   stdout=output_buffer,
                                   indent=2,
                                   natural_foreign=True,
                                   natural_primary=True)
                        
                        # Get the JSON string and write it with proper UTF-8 encoding
                        json_data = output_buffer.getvalue()
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(json_data)
                    else:
                        # No apps selected, create empty backup
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write('[]')
                
                # Update backup record
                backup.file_path = file_path
                backup.file_size = os.path.getsize(file_path)
                backup.status = 'completed'
                backup.save()
                
                messages.success(request, f'Sauvegarde "{backup.name}" créée avec succès!')
                
            except Exception as e:
                backup.status = 'failed'
                backup.error_message = str(e)
                backup.save()
                messages.error(request, f'Erreur lors de la création de la sauvegarde: {e}')
            
            return redirect('backup:dashboard')
    else:
        form = BackupForm()
    
    return render(request, 'backup/create_backup.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def download_backup(request, backup_id):
    backup = get_object_or_404(BackupRecord, id=backup_id)
    
    if not backup.file_exists:
        messages.error(request, 'Fichier de sauvegarde introuvable.')
        return redirect('backup:list')
    
    try:
        with open(backup.file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/json; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(backup.file_path)}"'
            return response
    except Exception as e:
        messages.error(request, f'Erreur lors du téléchargement: {e}')
        return redirect('backup:list')

def _perform_restore(file_path, request):
    """Helper function to perform database restore"""
    User = get_user_model()
    
    # Fix encoding issues first
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        # Handle files with latin-1 encoding (common for French text)
        with open(file_path, 'r', encoding='latin-1') as f:
            data = json.load(f)
        # Re-save with proper UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    try:
        # Strategy 1: Try loading data with database reset
        call_command('flush', interactive=False, verbosity=0)
        call_command('migrate', verbosity=0)
        call_command('loaddata', file_path, verbosity=0)
        
        # Ensure admin user exists
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='admin'
            )
        
        return True, None
        
    except Exception as e:
        return False, str(e)

@login_required
@user_passes_test(is_admin)
def restore_backup(request):
    if request.method == 'POST':
        form = RestoreForm(request.POST, request.FILES)
        if form.is_valid():
            restore_record = RestoreRecord(
                file_name=request.FILES['backup_file'].name,
                restored_by=request.user,
                status='processing'
            )
            restore_record.save()
            
            temp_path = None
            try:
                # Save uploaded file temporarily with proper encoding
                with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as temp_file:
                    for chunk in request.FILES['backup_file'].chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                
                # Validate JSON with encoding fallback
                try:
                    with open(temp_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except UnicodeDecodeError:
                    # Try with latin-1 encoding for French characters
                    with open(temp_path, 'r', encoding='latin-1') as f:
                        data = json.load(f)
                    # Re-save with proper UTF-8 encoding
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Perform restore
                success, error = _perform_restore(temp_path, request)
                
                if success:
                    restore_record.status = 'completed'
                    restore_record.save()
                    messages.success(request, 'Restauration effectuée avec succès!')
                else:
                    raise Exception(error)
                
            except Exception as e:
                restore_record.status = 'failed'
                restore_record.error_message = str(e)
                restore_record.save()
                messages.error(request, f'Erreur lors de la restauration: {e}')
            
            finally:
                # Cleanup temporary file
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
            return redirect('backup:dashboard')
    else:
        form = RestoreForm()
    
    return render(request, 'backup/restore_backup.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def restore_from_backup(request):
    if request.method == 'POST':
        form = BackupSelectForm(request.POST)
        if form.is_valid():
            backup = form.cleaned_data['backup_record']
            
            restore_record = RestoreRecord(
                backup_record=backup,
                file_name=os.path.basename(backup.file_path),
                restored_by=request.user,
                status='processing'
            )
            restore_record.save()
            
            try:
                if not backup.file_exists:
                    raise Exception("Fichier de sauvegarde introuvable")
                
                # Perform restore
                success, error = _perform_restore(backup.file_path, request)
                
                if success:
                    restore_record.status = 'completed'
                    restore_record.save()
                    messages.success(request, f'Restauration de "{backup.name}" effectuée avec succès!')
                else:
                    raise Exception(error)
                
            except Exception as e:
                restore_record.status = 'failed'
                restore_record.error_message = str(e)
                restore_record.save()
                messages.error(request, f'Erreur lors de la restauration: {e}')
            
            return redirect('backup:dashboard')
    else:
        form = BackupSelectForm()
    
    return render(request, 'backup/restore_from_backup.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_backup(request, backup_id):
    backup = get_object_or_404(BackupRecord, id=backup_id)
    
    if request.method == 'POST':
        try:
            # Delete file if exists
            if backup.file_exists:
                os.remove(backup.file_path)
            
            backup_name = backup.name
            backup.delete()
            messages.success(request, f'Sauvegarde "{backup_name}" supprimée avec succès!')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {e}')
        
        return redirect('backup:list')
    
    return render(request, 'backup/delete_backup.html', {'backup': backup})

@login_required
@user_passes_test(is_admin)
def backup_status(request, backup_id):
    backup = get_object_or_404(BackupRecord, id=backup_id)
    return JsonResponse({
        'status': backup.status,
        'error_message': backup.error_message,
        'file_size': backup.file_size_mb
    })