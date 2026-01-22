# Total costos indirectos
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from django.db import transaction
from modulo import models
from django.db.models import Sum
from modulo.forms import Total_Costos_IndirectosForm,DetalleCostosIndirectosForm,DetalleCostosIndirectosFormOpcion2
from modulo.models import Total_Costos_Indirectos,Detalle_Costos_Indirectos,Costos_Indirectos
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_total_costos_indirectos')
def total_costos_indirectos_index(request):
    try:
        # Obtener los datos de la base de datos
        total_costos_indirectos_data = Total_Costos_Indirectos.objects.all()

        # Pasar los datos al contexto
        return render(request, 'TotalCostosIndirectos/TotalCostosIndirectosIndex.html', {
            'total_costos_indirectos_data': total_costos_indirectos_data
        })
    except Exception as e:
        return render(request, 'TotalCostosIndirectos/TotalCostosIndirectosIndex.html', {
            'error_message': f'Error al cargar los datos: {str(e)}'
        })

@login_required
@verificar_permiso('can_manage_total_costos_indirectos')
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

    return render(request, 'TotalCostosIndirectos/TotalCostosIndirectosCrearDetalle.html', {'form': form, 'total_costos': total_costos})

@login_required
@verificar_permiso('can_manage_total_costos_indirectos')
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
    return render(request, 'TotalCostosIndirectos/TotalCostosIndirectosForm.html', {'form': form})

@login_required
@verificar_permiso('can_manage_total_costos_indirectos')
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

@login_required
@verificar_permiso('can_manage_total_costos_indirectos')
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
            "id": d["Id"],
            "Anio": d["Anio"],
            "Mes": d["Mes"],
            "CostosId": d["CostosId"],  # ✅ Mantiene el mismo nombre esperado
            "CostoNombre": d["CostosId__Costo"],  # 🔥 Agregamos el nombre del costo
            "Valor": d["Valor"]
        }
        for d in detalles_queryset
    ]
    print("Detalles después de procesarlos:")
    print(detalles)
    costos_disponibles = list(Costos_Indirectos.objects.values("CostoId", "Costo"))
    print("Costos disponibles:")
    print(costos_disponibles)
    response_data = {
        "detalles": detalles,
        "costos_disponibles": costos_disponibles
    }

    # 🔥 Imprime la respuesta final antes de enviarla
    print("Datos enviados en la respuesta JSON:")
    print(response_data)

    return JsonResponse(response_data)

@login_required
@verificar_permiso('can_manage_total_costos_indirectos')
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

@login_required
@verificar_permiso('can_manage_total_costos_indirectos')
@csrf_exempt
def total_costos_indirectos_editar(request):
    if request.method == 'POST':
        try:
            # Parsear los datos enviados desde el cliente
            data = json.loads(request.body)
            print(f"Datos recibidos: {data}")

            # Obtener los valores enviados
            detalle_id = data.get('id')
            anio = data.get('Anio')
            mes = data.get('Mes')
            valor = data.get('Valor')

            # Validar que los datos sean correctos
            if not detalle_id or not anio or not mes or valor is None:
                print("❌ Error: Datos incompletos.")
                return JsonResponse({'status': 'error', 'message': 'Datos incompletos.'}, status=400)

            # Buscar el registro correspondiente en la base de datos
            print(f"Buscando Total_Costos_Indirectos con ID={detalle_id}")
            total_costo = get_object_or_404(Total_Costos_Indirectos, id=detalle_id)

            # Actualizar los valores
            print(f"Actualizando Total_Costos_Indirectos con Total={valor}")
            total_costo.Anio = anio
            total_costo.Mes = mes
            total_costo.Total = valor
            total_costo.save()

            print("✅ Total de costos indirectos actualizado correctamente.")
            return JsonResponse({'status': 'success', 'message': 'Total de costos indirectos actualizado correctamente.'})
        except Total_Costos_Indirectos.DoesNotExist:
            print("❌ Error: Registro no encontrado.")
            return JsonResponse({'status': 'error', 'message': 'Registro no encontrado.'}, status=404)
        except json.JSONDecodeError:
            print("❌ Error: Error al decodificar JSON.")
            return JsonResponse({'status': 'error', 'message': 'Error al decodificar JSON.'}, status=400)
        except Exception as e:
            # Registrar el error en los logs del servidor
            print(f"❌ Error interno: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Error interno: {str(e)}'}, status=500)
    else:
        print("❌ Error: Método no permitido.")
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)