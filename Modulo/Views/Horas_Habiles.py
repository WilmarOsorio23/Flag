from django.contrib import messages
import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Modulo.forms import HorasHabilesForm
from Modulo.models import Horas_Habiles, Tiempos_Cliente, TiemposConcepto

def horas_habiles_index(request):
    horas_habiles = Horas_Habiles.objects.all()
    return render(request, 'Horas_Habiles/horas_habiles_index.html', {'horas_habiles': horas_habiles})

def horas_habiles_crear(request):
    if request.method == 'POST':
        form = HorasHabilesForm(request.POST)
        if form.is_valid():
            max_id = Horas_Habiles.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo = form.save(commit=False)
            nuevo.id = new_id  # Asignar el nuevo ID manualmente
            nuevo.save()
            return redirect('horas_habiles_index')
    else:
        form = HorasHabilesForm()
    return render(request, 'Horas_Habiles/horas_habiles_crear.html', {'form': form})

@csrf_exempt
def horas_habiles_editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            horas_habiles = get_object_or_404(Horas_Habiles, id=id)
            form = HorasHabilesForm(data, instance=horas_habiles)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Horas_Habiles.DoesNotExist:
            return JsonResponse({'error': 'Datos no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def horas_habiles_eliminar(request):
    if request.method == 'POST':
        ids = request.POST.get('items_to_delete', '').split(',')
        if ids:
            Horas_Habiles.objects.filter(id__in=ids).delete()
            messages.success(request, 'Los elementos seleccionados han sido eliminados correctamente.')
        else:
            messages.error(request, 'No se seleccionaron elementos para eliminar.')
        return redirect('horas_habiles_index')
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        items = data.get('data', [])

        # Verifica si están relacionados
        relacionados = []
        for item in items:
            anio = item.get('anio')
            mes = item.get('mes')
            if (
                Tiempos_Cliente.objects.filter(Anio=anio, Mes=mes).exists() or
                TiemposConcepto.objects.filter(Anio=anio, Mes=mes).exists()
            ):
                relacionados.append(item.get('id'))

        if relacionados:
            return JsonResponse({
                'isRelated': True,
                'ids': relacionados
            })
        else:
            return JsonResponse({'isRelated': False})
    return JsonResponse({'error': 'Datos no permitidos'}, status=405)

def horas_habiles_descargar_excel(request):
    # Verifica si la solicitud es POST
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete')  # Asegúrate de que este es el nombre correcto del campo
        # Convierte la cadena de IDs en una lista de enteros
    
        item_ids = list(map(int, item_ids.split (',')))  # Cambiado aquí
        Datos = Horas_Habiles.objects.filter(id__in=item_ids)

        # Crea una respuesta HTTP con el tipo de contenido de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Horas_Habiles.xlsx"'

        data = []
        for dato in Datos:
            data.append([dato.id, dato.Anio, dato.Mes, dato.Dias_Habiles, dato.Horas_Laborales,])

        df = pd.DataFrame(data, columns=['Id', 'Año', 'Mes', 'Dias Habiles', 'Horas Laborales'])
        df.to_excel(response, index=False)

        return response

    return redirect('horas_habiles_index')