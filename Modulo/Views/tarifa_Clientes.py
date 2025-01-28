# Tarifa Clientes
import pandas as pd
from django.shortcuts import get_object_or_404, redirect, render
from Modulo.forms import Tarifa_ClientesForm
from Modulo.models import Tarifa_Clientes
from django.db import models
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
import json


def tarifa_clientes_index(request):
    tarifa_clientes_data = Tarifa_Clientes.objects.all()
    return render(request, 'tarifa_clientes/tarifa_clientes_index.html', {'tarifa_clientes_data': tarifa_clientes_data})    

def tarifa_clientes_crear(request):
   if request.method == 'POST':
        form = Tarifa_ClientesForm(request.POST)
        if form.is_valid():
            max_id = Tarifa_Clientes.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_tarifa_cliente = form.save(commit=False)
            nuevo_tarifa_cliente.id = new_id
            nuevo_tarifa_cliente.save()
            return redirect('tarifa_clientes_index')
   else:
        form = Tarifa_ClientesForm()
   return render(request, 'Tarifa_Clientes/Tarifa_Clientes_form.html', {'form': form})   


def tarifa_clientes_editar(request, id):
     print("llego hasta editar")
     if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tarifa = get_object_or_404( Tarifa_Clientes, pk=id)
            tarifa.valorHora = data.get('valorHora', tarifa.valorHora)
            tarifa.valorDia = data.get('valorDia', tarifa.valorDia)
            tarifa.valorMes = data.get('valorMes', tarifa.valorMes)
            tarifa.bolsaMes= data.get('bolsaMes',tarifa.bolsaMes)
            tarifa.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Tarifa_Clientes.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
     else:
        return JsonResponse({'error': 'Método no permitido'}, status=405) 

def tarifa_clientes_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Tarifa_Clientes.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los elementos seleccionados se han eliminado correctamente.')
    return redirect('tarifa_clientes_index')


def tarifa_clientes_descargar_excel(request):   
     if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                detalle = Tarifa_Clientes.objects.get(pk=item_id)
                detalles_data.append([
                    detalle.id,
                    detalle.clienteId.Nombre_Cliente,
                    detalle.lineaId.Linea,
                    detalle.moduloId.Modulo,
                    detalle.anio,
                    detalle.mes,
                    detalle.valorHora,
                    detalle.valorDia,
                    detalle.valorMes,
                    detalle.bolsaMes,
                    detalle.monedaId.Nombre
                ])
            except Tarifa_Clientes.DoesNotExist:
                print(f"detalle con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not detalles_data:
            return HttpResponse("No se encontraron registros de tarifas de consultores.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(detalles_data, columns=['Id','Cliente','Linea','Modulo','Año','Mes','Valor Hora','Valor Dia','Valor Mes','Bolsa','Moneda'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="TarifaClientes.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
     return response
