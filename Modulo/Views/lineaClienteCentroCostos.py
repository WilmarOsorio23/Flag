import json
import pandas as pd

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from Modulo.decorators import verificar_permiso
from Modulo.forms import LineaClienteCentroCostosForm
from Modulo.models import LineaClienteCentroCostos, Linea, Clientes, CentrosCostos


@login_required
@verificar_permiso('can_manage_linea_cliente_centrocostos')
def linea_cliente_centrocostos_index(request):
    lccc_data = (LineaClienteCentroCostos.objects
                 .select_related('linea', 'cliente', 'centro_costo')
                 .all())

    context = {
        'lccc_data': lccc_data,
        'lineas': Linea.objects.all().order_by('Linea'),
        'clientes': Clientes.objects.all().order_by('Nombre_Cliente'),
        'centros_costos': CentrosCostos.objects.all().order_by('codigoCeCo'),
    }
    return render(request, 'LineaClienteCentroCostos/linea_cliente_centrocostos_index.html', context)


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
                messages.error(request, 'Ya existe una relación con esa combinación (Línea/Cliente/CeCo).')
        else:
            messages.error(request, 'Formulario inválido. Revisa los campos.')
    else:
        form = LineaClienteCentroCostosForm()

    return render(request, 'LineaClienteCentroCostos/linea_cliente_centrocostos_form.html', {'form': form})


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
        ceco_id = data.get('CentroCostoId')

        if not (linea_id and cliente_id and ceco_id):
            return JsonResponse({'error': 'Faltan campos: LineaId, ClienteId, CentroCostoId.'}, status=400)

        # Validar existencia (evita FK inválidas)
        if not Linea.objects.filter(pk=linea_id).exists():
            return JsonResponse({'error': 'La Línea seleccionada no existe.'}, status=400)
        if not Clientes.objects.filter(pk=cliente_id).exists():
            return JsonResponse({'error': 'El Cliente seleccionado no existe.'}, status=400)
        if not CentrosCostos.objects.filter(pk=ceco_id).exists():
            return JsonResponse({'error': 'El Centro de Costos seleccionado no existe.'}, status=400)

        rel.linea_id = int(linea_id)
        rel.cliente_id = int(cliente_id)
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
    """
    Verificación genérica: si algún modelo tiene FK hacia LineaClienteCentroCostos,
    bloquea la eliminación.
    """
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

        # Si tiene objetos relacionados por reverse FK/M2M (cuando existan en el futuro)
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

        qs = (LineaClienteCentroCostos.objects
              .select_related('linea', 'cliente', 'centro_costo')
              .filter(id__in=ids))

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Linea_Cliente_CentroCostos.xlsx"'

        data = []
        for r in qs:
            data.append([
                r.id,
                r.linea.Linea,
                r.cliente.Nombre_Cliente,
                r.centro_costo.codigoCeCo,
                r.centro_costo.descripcionCeCo
            ])

        df = pd.DataFrame(data, columns=['Id', 'Linea', 'Cliente', 'CodigoCeCo', 'DescripcionCeCo'])
        df.to_excel(response, index=False)
        return response

    return redirect('linea_cliente_centrocostos_index')
