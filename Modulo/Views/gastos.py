# Vista Gastos
import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.contrib import messages
from Modulo.forms import GastoForm
from Modulo.models import Detalle_Gastos, Gastos
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_gastos')
def gasto_index(request):
    # Ordenar los gastos por el campo 'id' en orden ascendente
    gastos = Gastos.objects.all().order_by('GastoId')
    return render(request, 'Gastos/GastoIndex.html', {'gastos': gastos})   

@login_required
@verificar_permiso('can_manage_gastos')
def gasto_crear(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            max_id = Gastos.objects.all().aggregate(max_id=models.Max('GastoId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1 
            nuevo_gasto = form.save(commit=False)
            nuevo_gasto.GastoId = new_id
            nuevo_gasto.save()
            return redirect('gastos_index')
    else:
        form = GastoForm()
    return render(request, 'Gastos/GastoForm.html', {'form': form})

@login_required
@verificar_permiso('can_manage_gastos')
@csrf_exempt
def gasto_editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            gasto = get_object_or_404(Gastos, GastoId=id)
            gasto.Gasto = data.get('Gasto', gasto.Gasto)  # Actualiza solo si está presente
            gasto.save()
            return JsonResponse({'status': 'success'})
        except Gastos.DoesNotExist:
            return JsonResponse({'status': 'error', 'errors': ['Gasto no encontrado']})
        except ValueError as ve:
            return JsonResponse({'status': 'error', 'errors': ['Error al procesar los datos: ' + str(ve)]})
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': ['Error desconocido: ' + str(e)]})
    return JsonResponse({'status': 'error', 'error': 'Método no permitido'})

@login_required
@verificar_permiso('can_manage_gastos')
def gasto_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Gastos.objects.filter(GastoId__in=item_ids).delete()
        messages.success(request, 'Los Gastos seleccionados se han eliminado correctamente.')
        return redirect('gastos_index')
    return redirect('gastos_index')

@login_required
@verificar_permiso('can_manage_gastos')
def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Detalle_Gastos.objects.filter(GastosId=id).exists()
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

@login_required
@verificar_permiso('can_manage_gastos')
def gasto_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete') 
        # Convierte la cadena de IDs en una lista de enteros
    
        item_ids = list(map(int, item_ids.split (',')))  # Cambiado aquí
        gasto_data = Gastos.objects.filter(GastoId__in=item_ids)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="gastos.xlsx"'

        data = []
        for gasto in gasto_data:
            data.append([gasto.GastoId, gasto.Gasto])

        df = pd.DataFrame(data, columns=['GastoId', 'Gasto'])
        df.to_excel(response, index=False)

        return response

    return redirect('gastos_index')