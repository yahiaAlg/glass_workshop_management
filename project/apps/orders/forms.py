from django import forms
from .models import Order, OrderItem
from apps.customers.models import Customer
from apps.inventory.models import GlassProduct

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'delivery_date', 'status', 'delivery_address', 'installation_required', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'installation_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'width', 'height', 'quantity', 'unit_price', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = GlassProduct.objects.filter(status='active')
        # Set initial value for quantity
        if not self.instance.pk:  # For new items only
            self.fields['quantity'].initial = 1