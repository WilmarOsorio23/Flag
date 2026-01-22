from django.contrib import messages
import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from modulo.forms import CargosForm
from modulo.models import Consultores, Empleado,Cargos
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_cargos')
def cargos_index(request):
    # Ordenar los módulos por el campo 'id' en orden ascendente
    lista  = Cargos.objects.all().order_by('CargoId')
    return render(request, 'Cargos/CargosIndex.html', {'Cargos': lista})

@login_required
@verificar_permiso('can_manage_cargos')
def crear(request):
    if request.method == 'POST':
        form = CargosForm(request.POST)
        if form.is_valid():
            max_id = Cargos.objects.all().aggregate(max_id=models.Max('CargoId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_modulo = form.save(commit=False)
            nuevo_modulo.CargoId = new_id
            nuevo_modulo.save()
            
            return redirect('cargos_index')
    else:
        form = CargosForm()
    return render(request, 'Cargos/CargosCrear.html', {'form': form})

@login_required
@verificar_permiso('can_manage_cargos')
@csrf_exempt
def editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            modulo = get_object_or_404(Cargos, pk=id)
            modulo.Cargo = data.get('Cargo', modulo.Cargo)  # Actualiza solo si está presente
            modulo.save()
            return JsonResponse({'status': 'success'})
        except Cargos.DoesNotExist:
            return JsonResponse({'status': 'error', 'errors': ['Cargo no encontrado']})
        except ValueError as ve:
            return JsonResponse({'status': 'error', 'errors': ['Error al procesar los datos: ' + str(ve)]})
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': ['Error desconocido: ' + str(e)]})
    return JsonResponse({'status': 'error', 'error': 'Cargo no permitido'})
    
@login_required
@verificar_permiso('can_manage_cargos')
def eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Cargos.objects.filter(CargoId__in=item_ids).delete()
        messages.success(request, 'Los cargos seleccionados se han eliminado correctamente.')
        return redirect('cargos_index')
    return redirect('cargos_index')

@login_required
@verificar_permiso('can_manage_cargos')
def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Empleado.objects.filter(CargoId=id).exists()
            ): 
                relacionados.append(id)

        if relacionados:
            return JsonResponse({
                'isRelated': True,
                'ids': relacionados
            })
        else:
            return JsonResponse({'isRelated': False})
    return JsonResponse({'error': 'Cargo no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_cargos')
def descargar_excel(request):
    # Verifica si la solicitud es POST
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete')  # Asegúrate de que este es el nombre correcto del campo
        # Convierte la cadena de IDs en una lista de enteros
    
        item_ids = list(map(int, item_ids.split (',')))  # Cambiado aquí
        Datos = Cargos.objects.filter(CargoId__in=item_ids)

        # Crea una respuesta HTTP con el tipo de contenido de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Cargos.xlsx"'

        data = []
        for dato in Datos:
            data.append([dato.CargoId, dato.Cargo])

        df = pd.DataFrame(data, columns=['Id', 'Nombre'])
        df.to_excel(response, index=False)

        return response

    return redirect('cargos_index')
