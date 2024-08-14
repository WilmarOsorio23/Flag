from django import forms
from .models import Modulo

class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = '__all__'
        widgets = {
            'Nombre': forms.TextInput(attrs=
                {
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': 'Ingrese el nombre del módulo'
                }),
            
        }
