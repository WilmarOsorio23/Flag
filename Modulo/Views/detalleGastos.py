# Detalle gastos
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from modulo.forms import DetalleGastosForm
from modulo.models import Detalle_Gastos
from django.db import models
from django.contrib import messages
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_detalle_gastos')
def detalle_gastos_index(request):
    detalles = Detalle_Gastos.objects.all()
    print("Buscando plantilla en: Detalle_Gastos/detalle_gastos_index.html")
    return render(request, 'DetalleGastos/DetalleGastosIndex.html', {'detalles': detalles})

@login_required
@verificar_permiso('can_manage_detalle_gastos')
def detalle_gastos_crear(request):
    if request.method == 'POST':
        form = DetalleGastosForm(request.POST)
        if form.is_valid():
            max_id = Detalle_Gastos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_detalle_gasto = form.save(commit=False)
            nuevo_detalle_gasto.id = new_id
            nuevo_detalle_gasto.save()
            return redirect('detalle_gastos_index')
    else:
        form = DetalleGastosForm()
    return render(request, 'DetalleGastos/DetalleGastosForm.html', {'form': form})

@login_required
@verificar_permiso('can_manage_detalle_gastos')
def detalle_gastos_editar(request,id):
    print("llego hasta editar")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalle = get_object_or_404( Detalle_Gastos, pk=id)
            detalle.Valor = data.get('Valor', detalle.Valor)
            detalle.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Detalle_Gastos.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_detalle_gastos')
def detalle_gastos_eliminar(request):
     if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Detalle_Gastos.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
     return redirect('detalle_gastos_index')

@login_required
@verificar_permiso('can_manage_detalle_gastos')
def detalle_gastos_descargar_excel(request):
    if request.method == 'POST':
        items_selected = request.POST.get('items_to_download')
        items_selected = list(map(int, items_selected.split (','))) 

        detalleGastos = Detalle_Gastos.objects.filter(id__in=items_selected)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="DetalleGastos.xlsx"'

        data = []
        for detalle in detalleGastos:
            data.append([
                detalle.id,
                detalle.Anio,
                detalle.Mes,
                detalle.Valor,
                detalle.GastosId
            ])
        df = pd.DataFrame(data, columns=['Id','Anio','Mes','Valor','Gasto'])
        df.to_excel(response, index=False)
        return response
    return redirect('detalle_gastos_index')

