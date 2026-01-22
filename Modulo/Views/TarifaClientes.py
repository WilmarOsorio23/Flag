# Modulo/Views/tarifa_Clientes.py
import pandas as pd
import json

from django.shortcuts import get_object_or_404, redirect, render
from django.db import models
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from Modulo.forms import Tarifa_ClientesForm
from Modulo.models import Tarifa_Clientes
from Modulo.decorators import verificar_permiso


@login_required
@verificar_permiso('can_manage_tarifa_clientes')
def tarifa_clientes_index(request):
    tarifa_clientes_data = (
        Tarifa_Clientes.objects
        .select_related(
            'clienteId',
            'lineaId',
            'moduloId',
            'referenciaId',
            'centrocostosId',
            'monedaId'
        )
        .all()
    )

    form = Tarifa_ClientesForm()
    return render(
        request,
        'Tarifaclientes/Tarifaclientesindex.html',
        {'tarifa_clientes_data': tarifa_clientes_data, 'form': form},
    )


@login_required
@verificar_permiso('can_manage_tarifa_clientes')
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

    return render(request, 'TarifaClientes/TarifaClientesForm.html', {'form': form})


@login_required
@verificar_permiso('can_manage_tarifa_clientes')
def tarifa_clientes_editar(request, id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        tarifa = get_object_or_404(Tarifa_Clientes, pk=id)

        tarifa.valorHora = data.get('valorHora', tarifa.valorHora)
        tarifa.valorDia = data.get('valorDia', tarifa.valorDia)
        tarifa.valorMes = data.get('valorMes', tarifa.valorMes)
        tarifa.bolsaMes = data.get('bolsaMes', tarifa.bolsaMes)
        tarifa.iva = data.get('iva', tarifa.iva)
        tarifa.monedaId_id = data.get('moneda', tarifa.monedaId_id)
        tarifa.referenciaId_id = data.get('referencia', tarifa.referenciaId_id)
        tarifa.centrocostosId_id = data.get('centroCostos', tarifa.centrocostosId_id)
        tarifa.sitioTrabajo = data.get('sitioTrabajo', tarifa.sitioTrabajo)
        tarifa.valorBolsa = data.get('valorBolsa', tarifa.valorBolsa)

        tarifa.save()
        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)

    except Exception as e:
        # ✅ Esto te permite ver el error real en frontend (y no solo "Error al guardar...")
        return JsonResponse({'error': f'{type(e).__name__}: {str(e)}'}, status=400)


@login_required
@verificar_permiso('can_manage_tarifa_clientes')
def tarifa_clientes_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Tarifa_Clientes.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los elementos seleccionados se han eliminado correctamente.')
    return redirect('tarifa_clientes_index')


@login_required
@verificar_permiso('can_manage_tarifa_clientes')
def tarifa_clientes_descargar_excel(request):
    if request.method != 'POST':
        return HttpResponse("Método no permitido.", status=405)

    item_ids = request.POST.getlist('items_to_delete')
    if not item_ids:
        return HttpResponse("No se seleccionaron elementos para descargar.", status=400)

    qs = (
        Tarifa_Clientes.objects
        .filter(id__in=item_ids)
        .select_related('clienteId', 'lineaId', 'moduloId', 'monedaId', 'referenciaId', 'centrocostosId')
    )

    if not qs.exists():
        return HttpResponse("No se encontraron registros de tarifas de clientes.", status=404)

    detalles_data = []
    for detalle in qs:
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
            detalle.monedaId.Nombre,
            detalle.referenciaId.codigoReferencia,
            detalle.centrocostosId.codigoCeCo,
            detalle.iva,
            detalle.sitioTrabajo
        ])

    df = pd.DataFrame(detalles_data, columns=[
        'Id', 'Cliente', 'Linea', 'Modulo', 'Año', 'Mes', 'Valor Hora', 'Valor Dia', 'Valor Mes',
        'Bolsa', 'Moneda', 'Referencia', 'Centro de Costos', 'IVA', 'Sitio de Trabajo'
    ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="TarifaClientes.xlsx"'
    df.to_excel(response, index=False)
    return response
