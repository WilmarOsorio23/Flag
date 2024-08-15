from django import forms
from .models import Modulo, IPC

class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = '__all__'
        widgets = {
            'Nombre': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del módulo'
            }),
        }

class IPCForm(forms.ModelForm):
    class Meta:
        model = IPC
        fields = '__all__'
        widgets = {
            'anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
            'campo_numerico': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el Indice'
            }),
        }
        labels = {
            'anio': 'Año',
            'mes': 'Mes',
            'campo_numerico': 'Indice',
        }


