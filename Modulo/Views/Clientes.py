# Vista para la tabla Clientes
import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.db.models import Q
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
        # Obtener los IDs desde el formulario y verificar si no está vacío
        item_ids = request.POST.get('items_to_download', '').strip()
        
        if not item_ids:
            messages.error(request, "No se seleccionaron clientes para descargar.")
            return redirect('cliente_index')
        
        # Crear una lista de combinaciones de TipoDocumentoID y DocumentoId
        filter_params = []
        try:
            for item in item_ids.split(','):
                tipo_documento_id, documento_id = item.split('-')
                filter_params.append(Q(TipoDocumentoID=tipo_documento_id, DocumentoId=documento_id))
        except ValueError:
            messages.error(request, "El formato de los datos es incorrecto.")
            return redirect('cliente_index')

        # Filtrar los clientes utilizando las combinaciones
        clientes_data = Clientes.objects.filter(*filter_params)

        # Verificar si existen clientes seleccionados
        if not clientes_data.exists():
            messages.error(request, "No se encontraron clientes para descargar.")
            return redirect('cliente_index')

        # Preparar los datos para el DataFrame
        data = [
            [
                cliente.TipoDocumentoID.Nombre,  # Ajusta esto según el modelo relacionado si es necesario
                cliente.DocumentoId,
                cliente.Nombre_Cliente,
                cliente.Activo,
                cliente.Fecha_Inicio,
                cliente.Fecha_Retiro
            ]
            for cliente in clientes_data
        ]

        # Crear el DataFrame y exportar a Excel
        df = pd.DataFrame(data, columns=[
            'Tipo Documento', 'Documento ID', 'Nombre Cliente', 'Activo', 'Fecha Inicio', 'Fecha Retiro'
        ])

        # Configurar la respuesta para enviar el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="clientes.xlsx"'
        df.to_excel(response, index=False)

        return response

    # Redirigir si no es un método POST
    return redirect('cliente_index')