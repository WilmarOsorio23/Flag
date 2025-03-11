# Centros de Costos
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from Modulo.forms import CentrosCostosForm
from Modulo.models import CentrosCostos, Tarifa_Clientes
from django.contrib import messages
from django.db import models


def centros_costos_index(request):
    centros_costos_data = CentrosCostos.objects.all()
    return render(request, 'CentrosCostos/centros_costos_index.html', {'centros_costos_data': centros_costos_data})

def centros_costos_crear(request):
    if request.method == 'POST':
        form = CentrosCostosForm(request.POST)
        if form.is_valid():
            max_id = CentrosCostos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_centro_costo = form.save(commit=False)
            nuevo_centro_costo.id = new_id  # Asignar un nuevo CentroCostoId
            nuevo_centro_costo.save()
            return redirect('centros_costos_index')
    else:
        form = CentrosCostosForm()
    return render(request,'CentrosCostos/centros_costos_form.html', {'form': form})

def centros_costos_editar(request, id):
   if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            ceco = get_object_or_404( CentrosCostos, pk=id)
            
            ceco.codigoCeCo= data.get('Codigo',ceco.codigoCeCo)
            ceco.descripcionCeCo = data.get('Descripcion', ceco.descripcionCeCo)
            ceco.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})  
        except CentrosCostos.DoesNotExist:
            return JsonResponse({'error': 'centro costo no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
   else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
   
def centros_costos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        CentrosCostos.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'La referencia seleccionada se han eliminado correctamente.')
        return redirect('centros_costos_index')

def verificar_relaciones(request):
    print("llego a verificar relaciones de centros de costos")
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        print("esta es la data",data)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Tarifa_Clientes.objects.filter(centrocostosId=id).exists()
             ): 
                relacionados.append(id)

        if relacionados:
            return JsonResponse({
                'isRelated': True,
                'ids': relacionados
            })
        else:
            return JsonResponse({'isRelated': False})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def centros_costos_descargar_excel(request):
    if request.method == 'POST':
        centrocostos_ids = request.POST.get('items_to_download')
        centrocostos_ids = list(map(int, centrocostos_ids.split (','))) 
        centrocosto = CentrosCostos.objects.filter(id__in=centrocostos_ids)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Centros_Costos.xlsx"'

        data = []
        for centrocostos in centrocosto:
            data.append([centrocostos.id,
                         centrocostos.codigoCeCo,
                         centrocostos.descripcionCeCo])
        
        df = pd.DataFrame(data, columns=['Id','Codigo','Descripcion'])
        df.to_excel(response, index=False)

        return response
    return redirect('centros_costos_index')