# Tarifa de Consultores
import json
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.shortcuts import get_object_or_404, redirect, render
from modulo.forms import Tarifa_ConsultoresForm
from modulo.models import Tarifa_Consultores
from django.db import models
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required


@login_required
@verificar_permiso('can_manage_tarifa_consultores')
def tarifa_consultores_index(request):
    page_size = 100
    page = int(request.GET.get('page', 1))

    tarifa_consultores_qs = Tarifa_Consultores.objects.select_related(
        'documentoId', 'moduloId', 'clienteID', 'monedaId'
    ).all()

    total_registros = tarifa_consultores_qs.count()
    total_paginas = (total_registros + page_size - 1) // page_size
    tarifa_consultores = tarifa_consultores_qs[(page-1)*page_size:page*page_size]

    form = Tarifa_ConsultoresForm()
    return render(request, 'TarifaConsultores/TarifaConsultoresIndex.html', {
        'tarifa_consultores': tarifa_consultores,
        'form': form,
        'total_paginas': total_paginas,
        'pagina_actual': page,
        'total_registros': total_registros,
    })


@login_required
@verificar_permiso('can_manage_tarifa_consultores')
def tarifa_consultores_crear(request):
    if request.method == 'POST':
        form = Tarifa_ConsultoresForm(request.POST)
        if form.is_valid():
            max_id = Tarifa_Consultores.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1

            nuevo_tarifa_consultores = form.save(commit=False)
            nuevo_tarifa_consultores.id = new_id

            if not nuevo_tarifa_consultores.iva:
                nuevo_tarifa_consultores.iva = None
            if not nuevo_tarifa_consultores.rteFte:
                nuevo_tarifa_consultores.rteFte = None

            nuevo_tarifa_consultores.save()
            return redirect('tarifa_consultores_index')
    else:
        form = Tarifa_ConsultoresForm()

    return render(request, 'TarifaConsultores/TarifaConsultoresForm.html', {'form': form})


@login_required
@verificar_permiso('can_manage_tarifa_consultores')
@csrf_exempt
def tarifa_consultores_editar(request, idd):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tarifa = get_object_or_404(Tarifa_Consultores, pk=idd)

            tarifa.valorHora = data.get('valorHora', tarifa.valorHora)
            tarifa.valorDia = data.get('valorDia', tarifa.valorDia)
            tarifa.valorMes = data.get('valorMes', tarifa.valorMes)
            tarifa.monedaId_id = data.get('monedaId', tarifa.monedaId_id)
            tarifa.moduloId_id = data.get('moduloId', tarifa.moduloId_id)
            tarifa.iva = data.get('iva', tarifa.iva) or None
            tarifa.rteFte = data.get('rteFte', tarifa.rteFte) or None

            tarifa.save()
            return JsonResponse({'status': 'success'})
        except Tarifa_Consultores.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
@verificar_permiso('can_manage_tarifa_consultores')
def tarifa_consultores_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Tarifa_Consultores.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
    return redirect('tarifa_consultores_index')


@login_required
@verificar_permiso('can_manage_tarifa_consultores')
def tarifa_consultores_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')

        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)

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
                    detalle.valorMes,
                    detalle.iva,
                    detalle.rteFte
                ])
            except Tarifa_Consultores.DoesNotExist:
                print(f"detalle con ID {item_id} no encontrada.")

        if not detalles_data:
            return HttpResponse("No se encontraron registros de tarifas de consultores.", status=404)

        df = pd.DataFrame(detalles_data, columns=[
            'Id','Consultor documento','Consultor Nombre','Año','Mes',
            'Cliente','Valor Hora','Valor Dia','Valor Mes','IVA','RteFte'
        ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="TarifaConsultores.xlsx"'
        df.to_excel(response, index=False)
        return response

    return HttpResponse(status=405)
