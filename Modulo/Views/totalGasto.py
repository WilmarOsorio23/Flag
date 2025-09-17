# Total gastos
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from django.db.models import Sum
from Modulo.forms import TotalGastosForm,DetalleGastosFormOpcion2
from Modulo.models import Total_Gastos, Detalle_Gastos, Gastos
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

def total_gastos_index(request):
    try:
        # Obtener los datos de la base de datos
        total_gastos_data = Total_Gastos.objects.all()

        # Pasar los datos al contexto
        return render(request, 'Total_Gastos/total_gastos_index.html', {
            'total_gastos_data': total_gastos_data
        })
    except Exception as e:
        return render(request, 'Total_Gastos/total_gastos_index.html', {
            'error_message': f'Error al cargar los datos: {str(e)}'
        })
def crear_detalle_gastos(request, total_gastos_id):
    total_gastos = get_object_or_404(Total_Gastos, id=total_gastos_id)

    if request.method == 'POST':
        form = DetalleGastosFormOpcion2(request.POST)
        if form.is_valid():
            nuevo_detalle = form.save(commit=False)
            nuevo_detalle.Anio = total_gastos.Anio  # Hereda Año
            nuevo_detalle.Mes = total_gastos.Mes    # Hereda Mes
            nuevo_detalle.TotalGastos = total_gastos  # Relacionarlo
            nuevo_detalle.save()
            return redirect('total_gastos_index')  # O a donde quieras redirigir
    else:
        form = DetalleGastosFormOpcion2()
    return render(request, 'Total_gastos/total_gastos_crear_detalle.html', {'form': form, 'total_gastos': total_gastos})

def total_gastos_crear(request):
    if request.method == 'POST':
        form = TotalGastosForm(request.POST)
        if form.is_valid():
            max_id = Total_Gastos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_total_gasto = form.save(commit=False)
            nuevo_total_gasto.id = new_id  # Asignar un nuevo ID
            nuevo_total_gasto.Total = 0
            nuevo_total_gasto.save()
            return redirect('total_gastos_index')
    else:
        form = TotalGastosForm()
    return render(request, 'total_gastos/total_gastos_form.html', {'form': form})

@csrf_exempt
def total_gastos_eliminar(request):
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
                Total_Gastos.objects.filter(id__in=totales).delete()

            # Eliminar Detalles
            if detalles:
                #Capturar Año y Mes antes de eliminar
                detalles_eliminados_data = list(Detalle_Gastos.objects.filter(id__in=detalles).values('Anio', 'Mes'))
                Detalle_Gastos.objects.filter(id__in=detalles).delete()

                for detalle in detalles_eliminados_data:
                    actualizar_total(request, detalle['Anio'], detalle['Mes'])

            return JsonResponse({"success": True})
        
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Error en el formato JSON recibido."})
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido."})

def visualizar_detalle_gastos(request, id):
    total_seleccionado = get_object_or_404(Total_Gastos, id=id)

    detalles_queryset = Detalle_Gastos.objects.filter(
        Anio=total_seleccionado.Anio, 
        Mes=total_seleccionado.Mes
    ).values("id", "Anio", "Mes", "GastosId", "GastosId__Gasto", "Valor")

    # 🔥 Convertimos los detalles en una lista con el formato correcto
    detalles = [
        {
            "id": d["id"],
            "Anio": d["Anio"],
            "Mes": d["Mes"],
            "GastosId": d["GastosId"],  # ✅ Mantiene el mismo nombre esperado
            "GastoNombre": d["GastosId__Gasto"],  # 🔥 Agregamos el nombre del costo
            "Valor": d["Valor"]
        }
        for d in detalles_queryset
    ]
    print("Detalles después de procesarlos:")
    print(detalles)
    gastos_disponibles = list(Gastos.objects.values("GastoId", "Gasto"))
    print("Gastos disponibles:")
    print(gastos_disponibles)
    response_data = {
        "detalles": detalles,
        "gastos_disponibles": gastos_disponibles
    }

    # 🔥 Imprime la respuesta final antes de enviarla
    print("Datos enviados en la respuesta JSON:")
    print(response_data)

    return JsonResponse(response_data)
    
@csrf_exempt
def editar_detalles_gastos(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalles_actualizados = []

            for detalle in data['detalles']:
                detalle_id = detalle.get('id')
                if not detalle_id:
                    continue

                detalle_obj = get_object_or_404(Detalle_Gastos, id=detalle_id)

                # Actualizar campos
                detalle_obj.Anio = detalle.get('Anio')
                detalle_obj.Mes = detalle.get('Mes')
                detalle_obj.GastosId_id = detalle.get('GastosId_id')
                detalle_obj.Valor = detalle.get('Valor')
                detalle_obj.save()
                detalles_actualizados.append(detalle_id)

            return JsonResponse({"status": "success", "message": "Detalles actualizados correctamente.", "actualizados": detalles_actualizados})

        except Exception as e:
            return JsonResponse({"status": "error", "message": "Error al actualizar detalles.", "error": str(e)})

def actualizar_total(request, anio, mes):
    try:
        total = Detalle_Gastos.objects.filter(Anio=anio, Mes=mes).aggregate(Sum('Valor'))['Valor__sum'] or 0
                
        # Actualizar en la base de datos
        Total_Gastos.objects.filter(Anio=anio, Mes=mes).update(Total=total)

        actualizado = Total_Gastos.objects.get(Anio=anio, Mes=mes)
        
        return JsonResponse({"success": True, "total": total})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
            
@csrf_exempt
def total_gastos_editar(request):
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
            print(f"Buscando Total_Gastos con ID={detalle_id}")
            total_gasto = get_object_or_404(Total_Gastos, id=detalle_id)

            # Actualizar los valores
            print(f"Actualizando Total_Gastos con Total={valor}")
            total_gasto.Anio = anio
            total_gasto.Mes = mes
            total_gasto.Total = valor
            total_gasto.save()

            print("✅ Total de gastos actualizado correctamente.")
            return JsonResponse({'status': 'success', 'message': 'Total de gastos actualizado correctamente.'})
        except Total_Gastos.DoesNotExist:
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
    
def total_gastos_descargar_excel(request):
    if request.method == 'POST':
        items_selected = request.POST.get('items_to_download')
        items_selected = list(map(int, items_selected.split (','))) 

        totalGastos = Total_Gastos.objects.filter(id__in=items_selected)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Total_Gasto.xlsx"'

        data = []
        for totalgasto in totalGastos:
            data.append([
                totalgasto.id,
                totalgasto.Anio,
                totalgasto.Mes,
                totalgasto.Total,
            ])
        df = pd.DataFrame(data, columns=['Id','Año','Mes','Total'])
        df.to_excel(response, index=False)
        return response
    return redirect('total_gastos_index')

'''def total_gastos_eliminar(request):
     if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Total_Gastos.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
        return redirect('total_gastos_index')

    def total_gastos_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                Costo = Total_Gastos.objects.get(pk=item_id)
                detalles_data.append([
                    Costo.id,
                    Costo.Anio,
                    Costo.Mes,
                    Costo.Total,
                ])
            except Total_Gastos.DoesNotExist:
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
        response['Content-Disposition'] = 'attachment; filename="TotalGastos.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response

    return redirect('total_gastos_index')'''