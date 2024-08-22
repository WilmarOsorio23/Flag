import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from .models import Modulo
from .forms import ModuloForm
from .models import IPC
from .models import Clientes
from .forms import IPCForm
from .forms import ClientesForm
from .models import Consultores
from .forms import ConsultoresForm

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


        data = []
        for modulo in modulos:
            data.append([modulo.id, modulo.Nombre])

        df = pd.DataFrame(data, columns=['Id', 'Nombre'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Modulos.xlsx"'

        df.to_excel(response, index=False)

        return response

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

# Vista para la tabla Clientes
def clientes_index(request):
    clientes = Clientes.objects.all()
    return render(request, 'clientes/clientes_index.html', {'clientes': clientes})

def clientes_crear(request):
    if request.method == 'POST':
        form = ClientesForm(request.POST)
        if form.is_valid():
            max_id = Clientes.objects.all().aggregate(max_id=models.Max('ClienteId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_cliente = form.save(commit=False)
            nuevo_cliente.ClienteId = new_id
            nuevo_cliente.save()
            return redirect('clientes_index')
    else:
        form = ClientesForm()
    
    return render(request, 'clientes/clientes_form.html', {'form': form})


@csrf_exempt
def clientes_editar(request, tipo_documento_id, documento_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            cliente = Clientes.objects.get(TipoDocumentoID=tipo_documento_id, DocumentoId=documento_id)
            form = ClientesForm(data, instance=cliente)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Clientes.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def clientes_eliminar(request):
    if request.method == 'POST':
        cliente_ids = request.POST.getlist('cliente_ids')
        for id_pair in cliente_ids:
            tipo_documento_id, documento_id = id_pair.split('-')
            Clientes.objects.filter(TipoDocumentoID=tipo_documento_id, DocumentoId=documento_id).delete()
        return redirect('clientes_index')
    return redirect('clientes_index')

def clientes_descargar_excel(request):
    if request.method == 'POST':
        # Obtener los IDs desde el formulario
        item_ids = request.POST.get('items_to_download', '').split(',')
        
        # Filtrar los clientes con los IDs proporcionados
        clientes_data = Clientes.objects.filter(ClienteId__in=item_ids)

        # Preparar los datos para el DataFrame
        data = []
        for cliente in clientes_data:
            data.append([
                cliente.TipoDocumentoID, 
                cliente.DocumentoId, 
                cliente.Nombre_Cliente, 
                cliente.Activo, 
                cliente.Fecha_Inicio, 
                cliente.Fecha_Retiro
            ])

        # Crear el DataFrame y exportar a Excel
        df = pd.DataFrame(data, columns=[
            'Tipo Documento ID', 
            'Documento ID', 
            'Nombre Cliente', 
            'Activo', 
            'Fecha Inicio', 
            'Fecha Retiro'
        ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="clientes.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('clientes_index')

def consultores_index(request):
    consultores = Consultores.objects.all()
    return render(request, 'consultores/consultores_index.html', {'consultores': consultores})

def consultores_crear(request):
    if request.method == 'POST':
        form = ConsultoresForm(request.POST)
        if form.is_valid():
            nuevo_consultor = form.save()
            return redirect('consultores_index')
    else:
        form = ConsultoresForm()
    
    return render(request, 'consultores/consultores_form.html', {'form': form})

@csrf_exempt
def consultores_editar(request, tipo_documento_id, documento_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            consultor = Consultores.objects.get(TipoDocumentoID=tipo_documento_id, DocumentoId=documento_id)
            form = ConsultoresForm(data, instance=consultor)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Consultores.DoesNotExist:
            return JsonResponse({'error': 'Consultor no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def consultores_eliminar(request):
    if request.method == 'POST':
        consultor_ids = request.POST.getlist('consultor_ids')
        for id_pair in consultor_ids:
            tipo_documento_id, documento_id = id_pair.split('-')
            Consultores.objects.filter(TipoDocumentoID=tipo_documento_id, DocumentoId=documento_id).delete()
        return redirect('consultores_index')
    return redirect('consultores_index')

def consultores_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_download', '').split(',')
        consultores_data = Consultores.objects.filter(TipoDocumentoID__in=item_ids)

        data = []
        for consultor in consultores_data:
            data.append([
                consultor.TipoDocumentoID,
                consultor.DocumentoId,
                consultor.Nombre,
                consultor.Empresa,
                consultor.Profesion,
                consultor.Estado,
                consultor.Fecha_Ingreso,
                consultor.Fecha_Retiro,
            ])

        df = pd.DataFrame(data, columns=[
            'Tipo Documento ID',
            'Documento ID',
            'Nombre',
            'Empresa',
            'Profesión',
            'Estado',
            'Fecha Ingreso',
            'Fecha Retiro'
        ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="consultores.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('consultores_index')