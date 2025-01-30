# Clientes Contratos
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo.forms import ClientesContratosForm
from Modulo.models import ClientesContratos
from django.db import models
from django.contrib import messages

def clientes_contratos_index(request):
    clientes_contratos_data = ClientesContratos.objects.all()
    return render(request, 'clientes_contratos/clientes_contratos_index.html', {'clientes_contratos_data': clientes_contratos_data})

def clientes_contratos_crear(request):
    if request.method == 'POST':
        form = ClientesContratosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes_contratos_index')
    else:
        form = ClientesContratosForm()
    return render(request, 'clientes_contratos/clientes_contratos_form.html', {'form': form})


def clientes_contratos_editar(request, id):
    print("llego hasta editar")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            contrato = get_object_or_404( ClientesContratos, pk=id)
            contrato.FechaFin = data.get('FechaFin', contrato.FechaFin)
            contrato.Contrato = data.get('Contrato', contrato.Contrato)
            contrato.ContratoVigente = data.get('ContratoVigente', contrato.ContratoVigente)
            contrato.OC_Facturar = data.get('OC_Facturar', contrato.OC_Facturar)
            contrato.Parafiscales = data.get('Parafiscales', contrato.Parafiscales)
            contrato.HorarioServicio = data.get('HorarioServicio', contrato.HorarioServicio)
            contrato.FechaFacturacion = data.get('FechaFacturacion', contrato.FechaFacturacion)
            contrato.TipoFacturacion = data.get('TipoFacturacion', contrato.TipoFacturacion)
            contrato.Observaciones = data.get('Observaciones', contrato.Observaciones)
            contrato.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except ClientesContratos.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def clientes_contratos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        ClientesContratos.objects.filter(ClientesContratosId__in=item_ids).delete()
        messages.success(request, 'Los contratos seleccionados se han eliminado correctamente.')
    return redirect('clientes_contratos_index')

def clientes_contratos_descargar_excel(request):    
     if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                detalle = ClientesContratos.objects.get(pk=item_id)
                detalles_data.append([
                    detalle.ClientesContratosId,
                    detalle.ClienteId.Nombre_Cliente,
                    detalle.LineaId.Linea,
                    detalle.FechaInicio,
                    detalle.FechaFin,
                    detalle.Contrato,
                    detalle.ContratoVigente,
                    detalle.OC_Facturar,
                    detalle.Parafiscales,
                    detalle.HorarioServicio,
                    detalle.FechaFacturacion,
                    detalle.TipoFacturacion,
                    detalle.Observaciones,
                ])
            except ClientesContratos.DoesNotExist:
                print(f"contrato con ID {item_id} no encontrado.")
        
        # Si no hay datos para exportar
        if not detalles_data:
            return HttpResponse("No se encontraron registros de contratos.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(detalles_data, columns=['Id','Cliente','Linea','FechaInicio','FechaFin','Contrato','ContratoVigente','OC_Facturar','Parafiscales','HorarioServicio','FechaFacturacion','TipoFacturacion','Observaciones'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Contratos.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
     return response

