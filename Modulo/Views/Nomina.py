# Modulo/Views/Nomina.py
import json
import pandas as pd
from itertools import groupby

from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from Modulo.forms import NominaForm
from Modulo.models import Clientes, Empleado, Nomina
from Modulo.decorators import verificar_permiso


@login_required
@verificar_permiso('can_manage_nomina')
def nomina_index(request):
    """
    Lista de registros de nómina en vista compacta:
    - Agrupa por empleado
    - Rowspan para Empleado y Año dentro del bloque del empleado
    """
    qs = (
        Nomina.objects
        .select_related('Documento', 'Cliente')
        .all()
        .order_by('Documento__Nombre', 'Documento__Documento', '-Anio', 'Mes', 'NominaId')
    )

    nomina_rows = []

    # groupby requiere que el queryset esté ordenado por la misma llave del grouping
    for doc_id, doc_group in groupby(qs, key=lambda n: n.Documento_id):
        doc_list = list(doc_group)
        doc_span = len(doc_list)

        i = 0
        while i < len(doc_list):
            year = doc_list[i].Anio
            j = i
            while j < len(doc_list) and doc_list[j].Anio == year:
                j += 1
            year_span = j - i

            for k in range(i, j):
                nomina_rows.append({
                    'nomina': doc_list[k],
                    'show_doc': (k == 0),
                    'doc_rowspan': doc_span if (k == 0) else 0,
                    'show_year': (k == i),
                    'year_rowspan': year_span if (k == i) else 0,
                    'is_group_start': (k == 0),
                })

            i = j

    form = NominaForm()
    return render(
        request,
        'nomina/nomina_index.html',
        {
            'nomina_rows': nomina_rows,
            'form': form,
        },
    )


@login_required
@verificar_permiso('can_manage_nomina')
def nomina_crear(request):
    if request.method == 'POST':
        form = NominaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('nomina_index')
    else:
        form = NominaForm()
    return render(request, 'Nomina/nomina_form.html', {'form': form})


@login_required
@verificar_permiso('can_manage_nomina')
@require_POST
def nomina_editar(request, id):
    """
    Edita un registro puntual de nómina vía fetch (JSON).
    Solo actualiza Salario y Cliente.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)

    nomina = get_object_or_404(Nomina, pk=id)

    salario = data.get('Salario')
    if salario is not None:
        try:
            salario_str = str(salario).replace('.', '').replace(',', '.')
            nomina.Salario = salario_str
        except Exception:
            return JsonResponse({'error': 'Formato de salario no válido'}, status=400)

    cliente_id = data.get('Cliente')
    if cliente_id:
        cliente = get_object_or_404(Clientes, pk=cliente_id)
        nomina.Cliente = cliente

    nomina.save()
    return JsonResponse({'status': 'success'})


@login_required
@verificar_permiso('can_manage_nomina')
def nomina_eliminar(request):
    if request.method != 'POST':
        return redirect('nomina_index')

    item_ids = request.POST.getlist('items_to_delete')
    if item_ids:
        Nomina.objects.filter(pk__in=item_ids).delete()

    return redirect('nomina_index')


@login_required
@verificar_permiso('can_manage_nomina')
@require_POST
def verificar_relaciones(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)

    relacionados = []
    if relacionados:
        return JsonResponse({'isRelated': True, 'ids': relacionados})
    return JsonResponse({'isRelated': False})


@login_required
@verificar_permiso('can_manage_nomina')
def nomina_descargar_excel(request):
    if request.method != 'POST':
        return redirect('nomina_index')

    items_selected = request.POST.get('items_to_download', '')
    if not items_selected:
        return HttpResponse("No se seleccionaron elementos para descargar.", status=400)

    try:
        ids = list(map(int, items_selected.split(',')))
    except ValueError:
        return HttpResponse("IDs de nómina inválidos.", status=400)

    nominas = (
        Nomina.objects
        .select_related('Documento', 'Cliente')
        .filter(NominaId__in=ids)
    )

    if not nominas.exists():
        return HttpResponse("No se encontraron registros de nómina.", status=404)

    data = []
    for nomina in nominas:
        data.append([
            nomina.Anio,
            nomina.Mes,
            nomina.Documento.Documento if nomina.Documento else '',
            nomina.Documento.Nombre if nomina.Documento else '',
            nomina.Salario,
            nomina.Cliente.Nombre_Cliente if nomina.Cliente else '',
        ])

    df = pd.DataFrame(
        data,
        columns=['Año', 'Mes', 'Documento', 'Nombre Empleado', 'Salario', 'Cliente'],
    )

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Nomina.xlsx"'
    df.to_excel(response, index=False)
    return response


# =========================================================
# NUEVO: BULK COPY (ORIGEN -> DESTINO) con preview editable
# =========================================================

@login_required
@verificar_permiso('can_manage_nomina')
@require_POST
def nomina_bulk_preview(request):
    """
    Devuelve los registros del mes/año origen para armar preview en el modal.
    Soporta Mes como CharField ("01") o IntegerField (1).
    """
    try:
        data = json.loads(request.body)
        anio = int(str(data.get('anio')).strip())
        mes_int = int(str(data.get('mes')).strip())
    except Exception:
        return JsonResponse({'error': 'Parámetros inválidos (anio/mes).'}, status=400)

    if mes_int < 1 or mes_int > 12:
        return JsonResponse({'error': 'Mes inválido.'}, status=400)

    mes_2 = f"{mes_int:02d}"
    mes_1 = str(mes_int)

    mes_field = Nomina._meta.get_field('Mes')
    mes_type = mes_field.get_internal_type()

    qs = (
        Nomina.objects
        .select_related('Documento', 'Cliente')
        .filter(Anio=anio)
        .order_by('Documento__Nombre', 'Documento__Documento', 'NominaId')
    )

    # Si Mes es texto: busca "01" y también "1" por compatibilidad
    if mes_type in ("CharField", "TextField"):
        qs = qs.filter(Mes__in=[mes_2, mes_1])
    else:
        qs = qs.filter(Mes=mes_int)

    items = []
    for n in qs:
        items.append({
            'origin_nomina_id': n.NominaId,
            'empleado_id': n.Documento_id,
            'empleado_documento': (n.Documento.Documento if n.Documento else ''),
            'empleado_nombre': (n.Documento.Nombre if n.Documento else ''),
            'salario': str(n.Salario if n.Salario is not None else ''),
            'cliente_id': n.Cliente_id,
        })

    return JsonResponse({'items': items, 'count': len(items)})


@login_required
@verificar_permiso('can_manage_nomina')
@require_POST
def nomina_bulk_create(request):
    """
    Crea registros en el mes/año destino con salario/cliente editados por línea.
    Soporta Mes como CharField ("01") o IntegerField (1).
    """
    try:
        data = json.loads(request.body)
        destino = data.get('destino', {})
        mode = (data.get('mode') or 'skip').lower()
        items = data.get('items') or []

        d_anio = int(str(destino.get('anio')).strip())
        d_mes_int = int(str(destino.get('mes')).strip())
    except Exception:
        return JsonResponse({'error': 'Payload inválido.'}, status=400)

    if d_mes_int < 1 or d_mes_int > 12:
        return JsonResponse({'error': 'Mes destino inválido.'}, status=400)

    if mode not in ('skip', 'overwrite'):
        mode = 'skip'

    d_mes_2 = f"{d_mes_int:02d}"
    d_mes_1 = str(d_mes_int)

    mes_field = Nomina._meta.get_field('Mes')
    mes_type = mes_field.get_internal_type()

    # Valor que guardaremos en BD
    mes_for_save = d_mes_2 if mes_type in ("CharField", "TextField") else d_mes_int

    created = 0
    updated = 0
    skipped = 0
    errors = []

    with transaction.atomic():
        for idx, it in enumerate(items):
            try:
                empleado_id = int(it.get('empleado_id'))
                cliente_id = int(it.get('cliente_id'))
                salario = it.get('salario', '')

                salario_str = str(salario).replace('.', '').replace(',', '.').strip()
                if salario_str == '':
                    raise ValueError('Salario vacío')

                empleado = get_object_or_404(Empleado, pk=empleado_id)
                cliente = get_object_or_404(Clientes, pk=cliente_id)

                base_qs = Nomina.objects.filter(Anio=d_anio, Documento_id=empleado_id)

                if mes_type in ("CharField", "TextField"):
                    existing = base_qs.filter(Mes__in=[d_mes_2, d_mes_1]).first()
                else:
                    existing = base_qs.filter(Mes=d_mes_int).first()

                if existing:
                    if mode == 'overwrite':
                        existing.Salario = salario_str
                        existing.Cliente = cliente
                        existing.Mes = mes_for_save
                        existing.save()
                        updated += 1
                    else:
                        skipped += 1
                    continue

                Nomina.objects.create(
                    Anio=d_anio,
                    Mes=mes_for_save,
                    Documento=empleado,
                    Salario=salario_str,
                    Cliente=cliente,
                )
                created += 1

            except Exception as e:
                errors.append({'row': idx + 1, 'error': str(e)})

    return JsonResponse({
        'status': 'success',
        'created': created,
        'updated': updated,
        'skipped': skipped,
        'errors': errors,
        'mode': mode,
    })