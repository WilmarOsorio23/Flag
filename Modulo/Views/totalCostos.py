# Total costos indirectos
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from Modulo.forms import Total_Costos_IndirectosForm
from Modulo.models import Total_Costos_Indirectos
from django.db import models
from django.contrib import messages

def total_costos_indirectos_index(request):
    total_costos_indirectos_data = Total_Costos_Indirectos.objects.all()
    return render(request, 'Total_Costos_Indirectos/total_costos_indirectos_index.html', {'total_costos_indirectos_data': total_costos_indirectos_data})


def total_costos_indirectos_crear(request):
    if request.method == 'POST':
        form = Total_Costos_IndirectosForm(request.POST)
        if form.is_valid():
            max_id = Total_Costos_Indirectos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_total_costo_indirecto = form.save(commit=False)
            nuevo_total_costo_indirecto.id = new_id  # Asignar un nuevo ID
            nuevo_total_costo_indirecto.save()
            return redirect('total_costos_indirectos_index')
    else:
        form = Total_Costos_IndirectosForm()
    return render(request, 'Total_Costos_Indirectos/total_costos_indirectos_form.html', {'form': form})


def total_costos_indirectos_editar(request,id):
   print("llego hasta editar")
   if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalle = get_object_or_404( Total_Costos_Indirectos, pk=id)
            detalle.Total = data.get('Total', detalle.Total)
            detalle.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Total_Costos_Indirectos.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
   else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def total_costos_indirectos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Total_Costos_Indirectos.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
    return redirect('total_costos_indirectos_index')

def total_costos_indirectos_descargar_excel(request):
     if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                costo = Total_Costos_Indirectos.objects.get(pk=item_id)
                detalles_data.append([
                    costo.id,
                    costo.Anio,
                    costo.Mes,
                    costo.Total,
                ])
            except Total_Costos_Indirectos.DoesNotExist:
                print(f"detalle con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not detalles_data:
            return HttpResponse("No se encontraron registros de detalles costos indirectos.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(detalles_data, columns=['Id','Año','Mes','Total'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="TotalCostos.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
     return redirect('total_costos_indirectos_index')