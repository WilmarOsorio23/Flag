# Total gastos
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from Modulo.forms import TotalGastosForm
from Modulo.models import Total_Gastos
from django.db import models
from django.contrib import messages

def total_gastos_index(request):
    total_gastos_data = Total_Gastos.objects.all()
    return render(request, 'Total_gastos/total_gastos_index.html', {'total_gastos_data': total_gastos_data})

def total_gastos_crear(request):
    if request.method == 'POST':
        form = TotalGastosForm(request.POST)
        if form.is_valid():
            max_id = Total_Gastos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_total_gasto = form.save(commit=False)
            nuevo_total_gasto.id = new_id  # Asignar un nuevo ID
            nuevo_total_gasto.save()
            return redirect('total_gastos_index')
    else:
        form = TotalGastosForm()
    return render(request, 'total_gastos/total_gastos_form.html', {'form': form})

def total_gastos_editar(request,id):
    print("llego hasta editar")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalle = get_object_or_404( Total_Gastos, pk=id)
            detalle.Total = data.get('total', detalle.Total)
            detalle.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Total_Gastos.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def total_gastos_eliminar(request):
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

    return redirect('total_gastos_index')