# Historial Cargos
import json
from urllib import request
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo.forms import HistorialCargosForm
from Modulo.models import Historial_Cargos
from django.db import models
from django.contrib import messages

def historial_cargos_index(request):
    historial_cargos_data = Historial_Cargos.objects.all()
    return render(request, 'Historial_Cargos/Historial_Cargos_index.html', {'historial_cargos_data': historial_cargos_data})

def historial_cargos_crear(request):
    if request.method == 'POST':
        form = HistorialCargosForm(request.POST)
        if form.is_valid():
            max_id = Historial_Cargos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_detalle_gasto = form.save(commit=False)
            nuevo_detalle_gasto.id = new_id
            nuevo_detalle_gasto.save()
            return redirect('historial_cargos_index')
    else:
        form = HistorialCargosForm()
    return render(request, 'Historial_Cargos/Historial_Cargos_form.html', {'form': form})   

def historial_cargos_editar(request, id):
     print("llego hasta editar")
     if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalle = get_object_or_404( Historial_Cargos, pk=id)
            detalle.FechaInicio = data.get('FechaInicio', detalle.FechaInicio)
            detalle.FechaFin = data.get('FechaFin', detalle.FechaFin)
            detalle.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Historial_Cargos.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)

def historial_cargos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Historial_Cargos.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
    return redirect('historial_cargos_index')

def historial_cargos_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                cargo = Historial_Cargos.objects.get(pk=item_id)
                detalles_data.append([
                    cargo.id,
                    cargo.documentoId.Nombre,
                    cargo.cargoId,
                    cargo.FechaInicio,
                    cargo.FechaFin,
                ])
            except Historial_Cargos.DoesNotExist:
                print(f"detalle con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not detalles_data:
            return HttpResponse("No se encontraron registros de detalles costos indirectos.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(detalles_data, columns=['Id','Nombre Empleado','cargoId','FechaInicio','FechaFin'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="HistorialCargos.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
    return response