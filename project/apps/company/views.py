from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Company
from .forms import CompanyForm

@login_required
def company_profile(request):
    company = Company.objects.first()
    if not company:
        company = Company.objects.create(
            name="Ma Verrerie",
            business_type="Commerce de verre et installation",
            address="Adresse à définir",
            phone="Téléphone à définir",
            email="contact@example.com",
            tax_rate=0.00  # Default to 0% if no company exists
        )
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil de l\'entreprise mis à jour avec succès.')
            return redirect('company:profile')
    else:
        form = CompanyForm(instance=company)
    
    return render(request, 'company/profile.html', {'form': form, 'company': company})

