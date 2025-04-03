# Total costos indirectos
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from django.db import transaction
from Modulo import models
from django.db.models import Sum
from Modulo.forms import Total_Costos_IndirectosForm,DetalleCostosIndirectosForm,DetalleCostosIndirectosFormOpcion2
from Modulo.models import Total_Costos_Indirectos,Detalle_Costos_Indirectos,Costos_Indirectos
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

def total_costos_indirectos_index(request):
    total_costos_indirectos_data = Total_Costos_Indirectos.objects.all()
    detalles = None
    seleccionado = request.GET.get('seleccionado')  # Obtiene el ID seleccionado si lo hay

    if seleccionado:
        total_seleccionado = get_object_or_404(Total_Costos_Indirectos, id=seleccionado)
        detalles = Detalle_Costos_Indirectos.objects.filter(
            Anio=total_seleccionado.Anio, 
            Mes=total_seleccionado.Mes
        )  # Filtra los detalles según el Año y Mes
    
    return render(request, 'Total_Costos_Indirectos/total_costos_indirectos_index.html', {
        'total_costos_indirectos_data': total_costos_indirectos_data,
        'detalles': detalles,
        'seleccionado': seleccionado,
    })
def crear_detalle_costos(request, total_costos_id):
    total_costos = get_object_or_404(Total_Costos_Indirectos, id=total_costos_id)

    if request.method == 'POST':
        form = DetalleCostosIndirectosFormOpcion2(request.POST)
        if form.is_valid():
            nuevo_detalle = form.save(commit=False)
            nuevo_detalle.Anio = total_costos.Anio  # Hereda Año
            nuevo_detalle.Mes = total_costos.Mes    # Hereda Mes
            nuevo_detalle.TotalCostosIndirectos = total_costos  # Relacionarlo
            nuevo_detalle.save()
            return redirect('total_costos_indirectos_index')  # O a donde quieras redirigir
    else:
        form = DetalleCostosIndirectosFormOpcion2()

    return render(request, 'Total_Costos_Indirectos/total_costos_indirectos_crear_detalle.html', {'form': form, 'total_costos': total_costos})


def total_costos_indirectos_crear(request):
    if request.method == 'POST':
        form = Total_Costos_IndirectosForm(request.POST)
        if form.is_valid():
            max_id = Total_Costos_Indirectos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_total_costo_indirecto = form.save(commit=False)
            nuevo_total_costo_indirecto.id = new_id  # Asignar un nuevo ID
            nuevo_total_costo_indirecto.Total = 0
            nuevo_total_costo_indirecto.save()
            return redirect('total_costos_indirectos_index')
    else:
        form = Total_Costos_IndirectosForm()
    return render(request, 'Total_Costos_Indirectos/total_costos_indirectos_form.html', {'form': form})

@csrf_exempt
def total_costos_indirectos_eliminar(request):
    if request.method == "POST":
        try:
            raw_data = request.body.decode("utf-8")
            data = json.loads(raw_data)
            totales = data.get("totales", [])
            detalles = data.get("detalles", [])

            if not totales and not detalles:
                return JsonResponse({"success": False, "error": "No se seleccionó ningún elemento."})

                # Eliminar Totales
            if totales:
                Total_Costos_Indirectos.objects.filter(id__in=totales).delete()

            # Eliminar Detalles
            if detalles:
                #Capturar Año y Mes antes de eliminar
                detalles_eliminados_data = list(Detalle_Costos_Indirectos.objects.filter(Id__in=detalles).values('Anio', 'Mes'))
                Detalle_Costos_Indirectos.objects.filter(Id__in=detalles).delete()

                for detalle in detalles_eliminados_data:
                    actualizar_total(request, detalle['Anio'], detalle['Mes'])

            return JsonResponse({"success": True})
        
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Error en el formato JSON recibido."})
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido."})

def total_costos_indirectos_descargar_excel(request):
    if request.method == 'POST':
        items_selected = request.POST.get('items_to_download')
        items_selected = list(map(int, items_selected.split (','))) 

        costosIndirectos = Total_Costos_Indirectos.objects.filter(id__in=items_selected)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Total_Costos_Indirectos.xlsx"'

        data = []
        for costo in costosIndirectos:
            data.append([
                costo.id,
                costo.Anio,
                costo.Mes,
                costo.Total,
            ])
        df = pd.DataFrame(data, columns=['Id','Año','Mes','Total'])
        df.to_excel(response, index=False)
        return response
    return redirect('total_costos_indirectos_index')

def visualizar_detalle_costos(request, id):
    total_seleccionado = get_object_or_404(Total_Costos_Indirectos, id=id)

    detalles_queryset = Detalle_Costos_Indirectos.objects.filter(
        Anio=total_seleccionado.Anio, 
        Mes=total_seleccionado.Mes
    ).values("Id", "Anio", "Mes", "CostosId", "CostosId__Costo", "Valor")

    # 🔥 Convertimos los detalles en una lista con el formato correcto
    detalles = [
        {
            "Id": d["Id"],
            "Anio": d["Anio"],
            "Mes": d["Mes"],
            "CostosId": d["CostosId"],  # ✅ Mantiene el mismo nombre esperado
            "CostoNombre": d["CostosId__Costo"],  # 🔥 Agregamos el nombre del costo
            "Valor": d["Valor"]
        }
        for d in detalles_queryset
    ]

    costos_disponibles = list(Costos_Indirectos.objects.values("CostoId", "Costo"))

    return JsonResponse({
        "detalles": detalles,
        "costos_disponibles": costos_disponibles
    })

@csrf_exempt
def editar_detalles_costos(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalles_actualizados = []

            for detalle in data['detalles']:
                detalle_id = detalle.get('Id')
                if not detalle_id:
                    continue

                detalle_obj = get_object_or_404(Detalle_Costos_Indirectos, Id=detalle_id)

                # Actualizar campos
                detalle_obj.Anio = detalle.get('Anio')
                detalle_obj.Mes = detalle.get('Mes')
                detalle_obj.CostosId_id = detalle.get('CostosId_id')
                detalle_obj.Valor = detalle.get('Valor')
                detalle_obj.save()
                detalles_actualizados.append(detalle_id)

            return JsonResponse({"status": "success", "message": "Detalles actualizados correctamente.", "actualizados": detalles_actualizados})

        except Exception as e:
            return JsonResponse({"status": "error", "message": "Error al actualizar detalles.", "error": str(e)})
        
def actualizar_total(request, anio, mes):
    try:
        total = Detalle_Costos_Indirectos.objects.filter(Anio=anio, Mes=mes).aggregate(Sum('Valor'))['Valor__sum'] or 0
                
        # Actualizar en la base de datos
        Total_Costos_Indirectos.objects.filter(Anio=anio, Mes=mes).update(Total=total)

        actualizado = Total_Costos_Indirectos.objects.get(Anio=anio, Mes=mes)
        
        return JsonResponse({"success": True, "total": total})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

'''
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
'''