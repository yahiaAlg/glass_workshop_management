from django import forms
from .models import GlassProduct, GlassType, GlassThickness, GlassColor, GlassFinish, Unit

class GlassProductForm(forms.ModelForm):
    class Meta:
        model = GlassProduct
        fields = '__all__'
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'glass_type': forms.Select(attrs={'class': 'form-select'}),
            'thickness': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.Select(attrs={'class': 'form-select'}),
            'finish': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to only show active options
        self.fields['glass_type'].queryset = GlassType.objects.filter(is_active=True)
        self.fields['thickness'].queryset = GlassThickness.objects.filter(is_active=True)
        self.fields['color'].queryset = GlassColor.objects.filter(is_active=True)
        self.fields['finish'].queryset = GlassFinish.objects.filter(is_active=True)
        self.fields['unit'].queryset = Unit.objects.filter(is_active=True)
        
        if self.instance and self.instance.pk:
            self.fields['code'].widget.attrs['readonly'] = True
        else:
            self.fields['code'].required = False