# Vista para la tabla Clientes
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from Modulo import models
from django.db import models
from Modulo.forms import ClientesForm
from Modulo.models import Clientes


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
        
        # Crear una lista para almacenar las combinaciones de TipoDocumentoID y DocumentoId
        filter_params = []
        for item in item_ids:
            tipo_documento_id, documento_id = item.split('-')
            filter_params.append((tipo_documento_id, documento_id))
        
        # Filtrar los clientes usando las combinaciones
        clientes_data = Clientes.objects.filter(
            (Q(TipoDocumentoID=tipo_documento_id) & Q(DocumentoId=documento_id)) for tipo_documento_id, documento_id in filter_params
        )

        # Preparar los datos para el DataFrame
        data = []
        for cliente in clientes_data:
            data.append([
                cliente.TipoDocumentoID.Nombre,  # Asumiendo que quieres mostrar el nombre del tipo de documento
                cliente.DocumentoId, 
                cliente.Nombre_Cliente, 
                cliente.Activo, 
                cliente.Fecha_Inicio, 
                cliente.Fecha_Retiro
            ])

        # Crear el DataFrame y exportar a Excel
        df = pd.DataFrame(data, columns=[
            'Tipo Documento', 
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

    return redirect('cliente_index')
