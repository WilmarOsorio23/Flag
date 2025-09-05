# Detalle costos indirectos
import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from Modulo.forms import DetalleCostosIndirectosForm
from Modulo.models import Detalle_Costos_Indirectos
from django.db import models
from django.contrib import messages
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_costos_indirectos')

def detalle_costos_indirectos_index(request):
    detalle_data = Detalle_Costos_Indirectos.objects.all()
    return render(request, 'detalle_costos_indirectos/detalle_costos_indirectos_index.html', {'detalle_data': detalle_data})

def detalle_costos_indirectos_crear(request):
     if request.method == 'POST':
        form = DetalleCostosIndirectosForm(request.POST)
        if form.is_valid():
            max_id =  Detalle_Costos_Indirectos.objects.all().aggregate(max_id=models.Max('Id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_DCI = form.save(commit=False)
            nuevo_DCI.Id= new_id
            nuevo_DCI.save()
            print("esto es:",nuevo_DCI)
            return redirect('detalle_costos_indirectos_index')
     else:
        form = DetalleCostosIndirectosForm()
     return render(request, 'Detalle_Costos_Indirectos/detalle_costos_indirectos_form.html', {'form': form})

def detalle_costos_indirectos_editar(request, id):
    print("llego hasta editar")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalle = get_object_or_404( Detalle_Costos_Indirectos, pk=id)
            detalle.Valor = data.get('Valor', detalle.Valor)
            detalle.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Detalle_Costos_Indirectos.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def detalle_costos_indirectos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Detalle_Costos_Indirectos.objects.filter(Id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
        return redirect('detalle_costos_indirectos_index')
    return redirect('detalle_costos_indirectos_index')

def detalle_costos_indirectos_descargar_excel(request):
    if request.method == 'POST':
        items_selected = request.POST.get('items_to_download')
        items_selected = list(map(int, items_selected.split (',')))

        detallesCostosIndirectos = Detalle_Costos_Indirectos.objects.filter(Id__in=items_selected)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="DetalleCostosIndirectos.xlsx"'

        data = []
        for detalle in detallesCostosIndirectos:
            data.append([
                detalle.Id,
                detalle.Anio,
                detalle.Mes,
                detalle.Valor,
                detalle.CostosId
            ])
        df = pd.DataFrame(data, columns=['Id','Anio','Mes','Valor','CostosId'])
        df.to_excel(response, index=False)
        return response
    return redirect('detalle_costos_indirectos_index')


'''def detalle_costos_indirectos_descargar_excel(request):
     if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                detalle = Detalle_Costos_Indirectos.objects.get(pk=item_id)
                detalles_data.append([
                    detalle.Id,
                    detalle.Anio,
                    detalle.Mes,
                    detalle.Valor,
                    detalle.CostosId 
                ])
            except Detalle_Costos_Indirectos.DoesNotExist:
                print(f"detalle con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not detalles_data:
            return HttpResponse("No se encontraron registros de detalles costos indirectos.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(detalles_data, columns=['Id','Anio','Mes','Valor','CostosId'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="DetalleCostosIndirectos.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response


     return redirect('detalle_costos_indirectos_index')
'''