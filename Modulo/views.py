from django.shortcuts import render
from django.http import HttpResponse
from .models import Modulo
# Create your views here.

def inicio(request):
    return render(request, 'paginas/Inicio.html')

def nosotros(request):
    return render(request, 'paginas/nosotros.html')

def Tablas(request):
    modulos = Modulo.objects.all()
    return render(request, 'Tablas/index.html', {'modulos': modulos})

def crear(request):
    return render(request, 'Tablas/crear.html')

def editar(request):
    return render(request, 'Tablas/editar.html')