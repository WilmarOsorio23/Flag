# Vista para la tabla Clientes
import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
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
def clientes_editar(request, id):
    print('aqui va bien', request)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente = get_object_or_404( Clientes, pk=id)
            cliente.Nombre_Cliente = data.get('Nombre_Cliente', cliente.Nombre_Cliente)           
            cliente.Fecha_Inicio= data.get('Fecha_Inicio', cliente.Fecha_Inicio)
            cliente.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
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
        item_ids = request.POST.get('items_to_delete', '')
        item_ids = item_ids.split(',')
        item_ids = [int(item) for item in item_ids if item.isdigit()]

        # Depuración: Verifica que ahora tienes una lista de enteros
        print(item_ids)

        clientes = Clientes.objects.filter(ClienteId__in=item_ids)
        
        # Verificar si se recibieron IDs
        if not clientes.exists():
            messages.error(request, "No se encontraron datos para descargar.")
            return redirect('clientes_index')
        
        # Consultar las nóminas usando las IDs
        data = []
        for cliente in clientes:
            data.append([
                cliente.ClienteId,
                cliente.Nombre_Cliente,
                cliente.Activo,
                cliente.Fecha_Inicio,
                cliente.Fecha_Retiro,                   
            ])
        
        # Crear DataFrame de pandas
        df = pd.DataFrame(data, columns=['ClienteID', 'Nombre', 'Activo', 'Fecha de Inicio', 'Fecha de Retiro'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Clientes.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
    return redirect('clientes_index')