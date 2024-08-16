import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Modulo
from .forms import ModuloForm
from .models import IPC
from .forms import IPCForm

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
<<<<<<< HEAD
            writer.writerow([modulo.id, modulo.Nombre])
        
=======
            data.append([modulo.id, modulo.Nombre])

        df = pd.DataFrame(data, columns=['Id', 'Nombre'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Modulos.xlsx"'

        df.to_excel(response, index=False)

>>>>>>> f42476379d64129f500ea4be4843f8f54e73b001
        return response

    # Si no es POST, redirige a la página de tablas
    return redirect('Tablas')

# Vista para la tabla IPC
def ipc_index(request):
    ipc_data = IPC.objects.all()
    return render(request, 'ipc/ipc_index.html', {'ipc_data': ipc_data})

def ipc_crear(request):
    if request.method == 'POST':
        form = IPCForm(request.POST)
        if form.is_valid():
            max_id = IPC.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_ipc = form.save(commit=False)
            nuevo_ipc.id = new_id
            nuevo_ipc.save()
            return redirect('ipc_index')
    else:
        form = IPCForm()
    return render(request, 'ipc/ipc_form.html', {'form': form})

def ipc_editar(request, id):
    ipc = get_object_or_404(IPC, id=id)

    if request.method == 'POST':
        form = IPCForm(request.POST, instance=ipc)
        if form.is_valid():
            ipc = form.save(commit=False)
            ipc.anio = ipc.anio
            ipc.mes = ipc.mes
            ipc.save()
            return redirect('ipc_index')
    else:
        form = IPCForm(instance=ipc)

    return render(request, 'ipc/ipc_form.html', {'form': form})

def ipc_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        IPC.objects.filter(id__in=item_ids).delete()
        return redirect('ipc_index')
    return redirect('ipc_index')

def ipc_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        ipc_data = IPC.objects.filter(id__in=item_ids)

        data = []
        for ipc in ipc_data:
            data.append([ipc.id, ipc.anio, ipc.mes, ipc.campo_numerico])

        df = pd.DataFrame(data, columns=['Id', 'Año', 'Mes', 'Campo Numérico'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="ipc.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('ipc_index')