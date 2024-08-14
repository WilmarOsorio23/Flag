import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from .models import Modulo
from .forms import ModuloForm

def inicio(request):
    return render(request, 'paginas/Inicio.html')

def nosotros(request):
    return render(request, 'paginas/nosotros.html')

def Tablas(request):
    # Ordenar los módulos por el campo 'id' en orden ascendente
    modulos = Modulo.objects.all().order_by('id')
    return render(request, 'Tablas/index.html', {'modulos': modulos})


def crear(request):
    if request.method == 'POST':
        form = ModuloForm(request.POST)
        if form.is_valid():
            max_id = Modulo.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_modulo = form.save(commit=False)
            nuevo_modulo.id = new_id
            nuevo_modulo.save()
            
            return redirect('Tablas')
    else:
        form = ModuloForm()
    return render(request, 'Tablas/crear.html', {'form': form})

def editar(request, id):
    modulo = get_object_or_404(Modulo, pk=id)
    if request.method == 'POST':
        form = ModuloForm(request.POST, instance=modulo)
        if form.is_valid():
            form.save()
            return redirect('Tablas')
    else:
        form = ModuloForm(instance=modulo)
    return render(request, 'Tablas/editar.html', {'form': form})

def eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Modulo.objects.filter(id__in=item_ids).delete()
        return redirect('Tablas')
    return redirect('Tablas')

def descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        modulos = Modulo.objects.filter(id__in=item_ids)

        # Crear un DataFrame con los datos de los módulos
        data = []
        for modulo in modulos:
            data.append([modulo.id, modulo.Nombre])

        df = pd.DataFrame(data, columns=['Id', 'Nombre'])

        # Crear una respuesta HTTP con el tipo de contenido de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="modulos_seleccionados.xlsx"'

        # Exportar el DataFrame a un archivo Excel
        df.to_excel(response, index=False)

        return response

    return redirect('Tablas')
