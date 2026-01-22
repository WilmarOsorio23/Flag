import json
import pandas as pd

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from modulo.decorators import verificar_permiso
from modulo.forms import LineaClienteCentroCostosForm
from modulo.models import LineaClienteCentroCostos, Linea, Clientes, CentrosCostos, Modulo


@login_required
@verificar_permiso('can_manage_linea_cliente_centrocostos')
def linea_cliente_centrocostos_index(request):
    lccc_data = (
        LineaClienteCentroCostos.objects
        .select_related('linea', 'cliente', 'modulo', 'centro_costo')
        .all()
    )

    context = {
        'lccc_data': lccc_data,
        'lineas': Linea.objects.all().order_by('Linea'),
        'clientes': Clientes.objects.all().order_by('Nombre_Cliente'),
        'modulos': Modulo.objects.all().order_by('Modulo'),
        'centros_costos': CentrosCostos.objects.all().order_by('codigoCeCo'),
    }
    return render(request, 'LineaClienteCentroCostos/LineaClienteCentroCostosIndex.html', context)


@login_required
@verificar_permiso('can_manage_linea_cliente_centrocostos')
def linea_cliente_centrocostos_crear(request):
    if request.method == 'POST':
        form = LineaClienteCentroCostosForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Relación creada correctamente.')
                return redirect('linea_cliente_centrocostos_index')
            except IntegrityError:
                messages.error(request, 'Ya existe una relación con esa combinación (Línea/Cliente/Módulo/CECO).')
        else:
            messages.error(request, 'Formulario inválido. Revisa los campos.')
    else:
        form = LineaClienteCentroCostosForm()

    return render(request, 'LineaClienteCentroCostos/LineaClienteCentroCostosForm.html', {'form': form})


@login_required
@verificar_permiso('can_manage_linea_cliente_centrocostos')
def linea_cliente_centrocostos_editar(request, id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body or '{}')
        rel = get_object_or_404(LineaClienteCentroCostos, pk=id)

        linea_id = data.get('LineaId')
        cliente_id = data.get('ClienteId')
        modulo_id = data.get('ModuloId')
        ceco_id = data.get('CentroCostoId')

        if not (linea_id and cliente_id and modulo_id and ceco_id):
            return JsonResponse(
                {'error': 'Faltan campos: LineaId, ClienteId, ModuloId, CentroCostoId.'},
                status=400
            )

        # Validar existencia
        if not Linea.objects.filter(pk=linea_id).exists():
            return JsonResponse({'error': 'La Línea seleccionada no existe.'}, status=400)
        if not Clientes.objects.filter(pk=cliente_id).exists():
            return JsonResponse({'error': 'El Cliente seleccionado no existe.'}, status=400)
        if not Modulo.objects.filter(pk=modulo_id).exists():
            return JsonResponse({'error': 'El Módulo seleccionado no existe.'}, status=400)
        if not CentrosCostos.objects.filter(pk=ceco_id).exists():
            return JsonResponse({'error': 'El Centro de Costos seleccionado no existe.'}, status=400)

        rel.linea_id = int(linea_id)
        rel.cliente_id = int(cliente_id)
        rel.modulo_id = int(modulo_id)
        rel.centro_costo_id = int(ceco_id)

        try:
            rel.save()
        except IntegrityError:
            return JsonResponse({'error': 'Ya existe una relación con esa combinación.'}, status=409)

        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)


@login_required
@verificar_permiso('can_manage_linea_cliente_centrocostos')
def linea_cliente_centrocostos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        LineaClienteCentroCostos.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los registros seleccionados se eliminaron correctamente.')
        return redirect('linea_cliente_centrocostos_index')
    return redirect('linea_cliente_centrocostos_index')


@login_required
@verificar_permiso('can_manage_linea_cliente_centrocostos')
def linea_cliente_centrocostos_verificar_relaciones(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    data = json.loads(request.body or '{}')
    ids = data.get('ids', [])

    relacionados = []
    for _id in ids:
        try:
            obj = LineaClienteCentroCostos.objects.get(pk=_id)
        except LineaClienteCentroCostos.DoesNotExist:
            continue

        for rel in obj._meta.related_objects:
            accessor = rel.get_accessor_name()
            manager = getattr(obj, accessor, None)
            if manager is not None and hasattr(manager, 'exists') and manager.exists():
                relacionados.append(_id)
                break

    if relacionados:
        return JsonResponse({'isRelated': True, 'ids': relacionados})
    return JsonResponse({'isRelated': False})


@login_required
@verificar_permiso('can_manage_linea_cliente_centrocostos')
def linea_cliente_centrocostos_descargar_excel(request):
    if request.method == 'POST':
        ids = request.POST.get('items_to_download', '')
        if not ids:
            return redirect('linea_cliente_centrocostos_index')

        ids = list(map(int, ids.split(',')))

        qs = (
            LineaClienteCentroCostos.objects
            .select_related('linea', 'cliente', 'modulo', 'centro_costo')
            .filter(id__in=ids)
        )

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Linea_Cliente_Modulo_CentroCostos.xlsx"'

        data_rows = []
        for r in qs:
            data_rows.append([
                r.id,
                r.linea.Linea,
                r.cliente.Nombre_Cliente,
                getattr(r.modulo, "Modulo", str(r.modulo)),
                r.centro_costo.codigoCeCo,
                r.centro_costo.descripcionCeCo
            ])

        df = pd.DataFrame(
            data_rows,
            columns=['Id', 'Linea', 'Cliente', 'Modulo', 'CodigoCeCo', 'DescripcionCeCo']
        )
        df.to_excel(response, index=False)
        return response

    return redirect('linea_cliente_centrocostos_index')