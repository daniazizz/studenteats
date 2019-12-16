from django import forms
from .models import EatingPlace


class EatingPlaceFrom(forms.ModelForm):
    class Meta:
        model = EatingPlace
        fields = ['name', 'address']
