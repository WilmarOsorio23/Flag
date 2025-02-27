# Tarifa de Consultores
import json
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.shortcuts import get_object_or_404, redirect, render
from Modulo.forms import Tarifa_ConsultoresForm
from Modulo.models import Tarifa_Consultores
from django.db import models
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
import json



def tarifa_consultores_index(request):
    tarifa_consultores = Tarifa_Consultores.objects.all()
    form=Tarifa_ConsultoresForm()
    return render(request, 'Tarifa_Consultores/tarifa_consultores_index.html', {'tarifa_consultores': tarifa_consultores, 'form': form})  

def tarifa_consultores_crear(request):
    if request.method == 'POST':
        form = Tarifa_ConsultoresForm(request.POST)
        if form.is_valid():
            max_id = Tarifa_Consultores.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_tarifa_consultores = form.save(commit=False)
            nuevo_tarifa_consultores.id = new_id
            nuevo_tarifa_consultores.save()
            return redirect('tarifa_consultores_index')
    else:
        form = Tarifa_ConsultoresForm()
    return render(request, 'Tarifa_Consultores/tarifa_consultores_form.html', {'form': form})   

@csrf_exempt
def tarifa_consultores_editar(request, idd):
    print("llego hasta editar")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tarifa = get_object_or_404(Tarifa_Consultores, pk=idd)
            tarifa.valorHora = data.get('valorHora', tarifa.valorHora)
            tarifa.valorDia = data.get('valorDia', tarifa.valorDia)
            tarifa.valorMes = data.get('valorMes', tarifa.valorMes)
            tarifa.monedaId_id = data.get('monedaId', tarifa.monedaId_id)
           
            
            tarifa.save()
            return JsonResponse({'status': 'success'})
        except Tarifa_Consultores.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405) 
    
def tarifa_consultores_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Tarifa_Consultores.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
    return redirect('tarifa_consultores_index')

def tarifa_consultores_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                detalle = Tarifa_Consultores.objects.get(pk=item_id)
                detalles_data.append([
                    detalle.id,
                    detalle.documentoId.Documento,
                    detalle.documentoId.Nombre,
                    detalle.anio,
                    detalle.mes,
                    detalle.clienteID.Nombre_Cliente,
                    detalle.valorHora,
                    detalle.valorDia,
                    detalle.valorMes
                ])
            except Tarifa_Consultores.DoesNotExist:
                print(f"detalle con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not detalles_data:
            return HttpResponse("No se encontraron registros de tarifas de consultores.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(detalles_data, columns=['Id','Consultor documento','Consultor Nombre','Año','Mes','Cliente','Valor Hora','Valor Dia','Valo Mes'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="TarifaConsultores.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
    return response

