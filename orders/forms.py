from django import forms
from .models import Category, MenuItem, Table, Order, OrderItem
from django.forms import inlineformset_factory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700',
                     'placeholder': 'e.g., Appetizers'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700', 'rows': 3}),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['category', 'name', 'description', 'price', 'image', 'is_available']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white'}),
            'name': forms.TextInput(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white', 'placeholder': 'Item name'}),
            'description': forms.Textarea(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white', 'rows': 2}),
            'price': forms.NumberInput(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white', 'step': '0.01'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_number', 'capacity', 'status']
        widgets = {
            'table_number': forms.NumberInput(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table', 'customer_name', 'party_size']
        widgets = {
            'table': forms.Select(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white'}),
            'customer_name': forms.TextInput(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white', 'placeholder': 'Guest Name'}),
            'party_size': forms.NumberInput(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white', 'min': 1, 'value': 1}),
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'table' in self.fields:
            self.fields['table'].queryset = Table.objects.exclude(status='FULL')
            self.fields['table'].label_from_instance = lambda obj: (
                f"Table {obj.table_number} ({obj.available_seats} of {obj.capacity} seats free)"
            )

OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    fields=['menu_item', 'quantity', 'special_instructions'],
    extra=3,            
    can_delete=True,
    widgets={
        'menu_item': forms.Select(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white'}),
        'quantity': forms.NumberInput(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white', 'min': 1}),
        'special_instructions': forms.TextInput(attrs={'class': 'w-full border border-black rounded px-3 py-2 text-sm bg-white', 'placeholder': 'Optional notes'}),
    }
)