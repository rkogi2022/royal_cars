from django import forms
from .models import Car

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['image', 'name', 'year', 'automation', 'price', 'rental_price']
