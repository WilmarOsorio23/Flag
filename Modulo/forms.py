from django import forms
from .models import Modulo

class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = '__all__'
