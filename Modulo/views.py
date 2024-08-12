import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
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
            form.save()
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

def descargar_csv(request):
    # Verifica si la solicitud es POST
    if request.method == 'POST':
        # Obtén los IDs seleccionados del formulario
        item_ids = request.POST.getlist('items_to_delete')

        # Filtra los módulos seleccionados
        modulos = Modulo.objects.filter(id__in=item_ids)
        
        # Crea una respuesta HTTP con el tipo de contenido de CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="modulos_seleccionados.csv"'

        # Crea un escritor CSV
        writer = csv.writer(response)
        
        # Escribe el encabezado
        writer.writerow(['Id', 'Nombre módulo'])

        # Escribe los datos de los módulos
        for modulo in modulos:
            writer.writerow([modulo.id, modulo.Nombre])
        
        return response

    # Si no es POST, redirige a la página de tablas
    return redirect('Tablas')
