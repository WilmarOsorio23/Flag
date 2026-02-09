# Modulo/Views/Nomina.py
import json
import re
import pandas as pd
from decimal import Decimal, InvalidOperation
from itertools import groupby
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from modulo.forms import NominaForm
from modulo.models import Clientes, Empleado, Nomina
from modulo.decorators import verificar_permiso


# =========================================================
# HELPERS
# =========================================================
def _D(v, default="0"):
    try:
        return Decimal(str(v if v is not None else default))
    except Exception:
        return Decimal(default)


def format_cop_for_input(value) -> str:
    """
    Formato es-CO para inputs (sin símbolo): 24850000 -> "24.850.000"
    """
    d = _D(value, "0")
    i = int(d)
    return f"{i:,}".replace(",", ".")


def parse_months_input(raw) -> list:
    """
    Acepta:
      - "1"        -> [1]
      - "01"       -> [1]
      - "1-12"     -> [1..12]
      - "1,2,3"    -> [1,2,3]
      - "1 2 3"    -> [1,2,3]
    """
    s = str(raw or "").strip()
    if not s:
        raise ValueError("Mes destino vacío")

    s = s.replace(" ", "")
    months = []

    if "-" in s:
        a, b = s.split("-", 1)
        a = int(a)
        b = int(b)
        if a < 1 or a > 12 or b < 1 or b > 12 or a > b:
            raise ValueError("Rango de meses inválido")
        months = list(range(a, b + 1))
    else:
        parts = [p for p in re.split(r"[,\s]+", s) if p]
        for p in parts:
            m = int(p)
            if m < 1 or m > 12:
                raise ValueError("Mes inválido")
            months.append(m)

    return sorted(set(months))


def parse_money_cop_to_decimal(value) -> Decimal:
    """
    Parsea salarios COP desde:
      "24850000"
      "24.850.000"
      "24,850,000"
      "$ 24.850.000"
      "24850000.00"
      "24.850.000,00"
    y retorna Decimal con 2 decimales (0.00).
    """
    s = str(value or "").strip()
    if not s:
        raise ValueError("Salario vacío")

    s = s.replace("COP", "").replace("$", "").strip()
    s = s.replace(" ", "")

    if re.fullmatch(r"\d+", s):
        return Decimal(s).quantize(Decimal("0.00"))

    last_dot = s.rfind(".")
    last_comma = s.rfind(",")

    if last_dot != -1 and last_comma != -1:
        if last_comma > last_dot:
            s = s.replace(".", "")
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    else:
        if "," in s:
            after = s.split(",")[-1]
            if len(after) in (1, 2):
                s = s.replace(".", "")
                s = s.replace(",", ".")
            else:
                s = s.replace(",", "")
        elif "." in s:
            after = s.split(".")[-1]
            if len(after) in (1, 2):
                s = s.replace(",", "")
            else:
                s = s.replace(".", "")

    s = re.sub(r"[^0-9.]", "", s)
    if s.count(".") > 1:
        last = s.rfind(".")
        s = s[:last].replace(".", "") + s[last:]

    try:
        return Decimal(s).quantize(Decimal("0.00"))
    except InvalidOperation:
        raise ValueError("Formato de salario no válido")


# =========================================================
# VISTAS CRUD
# =========================================================

@login_required
@verificar_permiso('can_manage_nomina')
def nomina_index(request):
    """
    ✅ Filtros por GET: año, mes, empleado (texto), cliente
    ✅ Bloques por empleado (alfabético)
    ✅ Separación por año dentro del empleado
    ✅ Nombre/Documento con rowspan por AÑO
    """
    # ----------------------------
    # 1) leer filtros
    # ----------------------------
    anio_raw = (request.GET.get("anio") or "").strip()
    mes_raw = (request.GET.get("mes") or "").strip()
    empleado_raw = (request.GET.get("empleado") or "").strip()
    cliente_raw = (request.GET.get("cliente") or "").strip()

    filters = {
        "anio": anio_raw,
        "mes": mes_raw,
        "empleado": empleado_raw,
        "cliente": cliente_raw,
    }

    # ----------------------------
    # 2) queryset base
    # ----------------------------
    qs = (
        Nomina.objects
        .select_related("Documento", "Cliente")
        .all()
    )

    # ----------------------------
    # 3) aplicar filtros
    # ----------------------------
    # Año
    if anio_raw:
        try:
            qs = qs.filter(Anio=int(anio_raw))
        except Exception:
            pass

    # Mes (soporta CharField "01" o IntegerField 1)
    if mes_raw:
        try:
            mes_int = int(str(mes_raw))
            if 1 <= mes_int <= 12:
                mes_2 = f"{mes_int:02d}"
                mes_1 = str(mes_int)

                mes_field = Nomina._meta.get_field("Mes")
                mes_type = mes_field.get_internal_type()

                if mes_type in ("CharField", "TextField"):
                    qs = qs.filter(Mes__in=[mes_2, mes_1])
                else:
                    qs = qs.filter(Mes=mes_int)
        except Exception:
            pass

    # Empleado (texto: nombre o documento)
    if empleado_raw:
        qs = qs.filter(
            Q(Documento__Nombre__icontains=empleado_raw) |
            Q(Documento__Documento__icontains=empleado_raw)
        )

    # Cliente
    if cliente_raw:
        try:
            qs = qs.filter(Cliente_id=int(cliente_raw))
        except Exception:
            pass

    # ----------------------------
    # 4) orden (alfabético por empleado + año/mes)
    # ----------------------------
    qs = qs.order_by(
        "Documento__Nombre",
        "Documento__Documento",
        "Documento_id",
        "-Anio",
        "Mes",
        "NominaId",
    )

    # ----------------------------
    # 5) construir rows (empleado -> años)
    # ----------------------------
    nomina_rows = []

    for doc_id, doc_group in groupby(qs, key=lambda n: n.Documento_id):
        doc_list = list(doc_group)

        i = 0
        while i < len(doc_list):
            year = doc_list[i].Anio
            j = i
            while j < len(doc_list) and doc_list[j].Anio == year:
                j += 1
            year_span = j - i

            for k in range(i, j):
                nomina_rows.append({
                    "nomina": doc_list[k],

                    # empleado por AÑO
                    "show_doc": (k == i),
                    "doc_rowspan": year_span if (k == i) else 0,

                    # año por bloque anual
                    "show_year": (k == i),
                    "year_rowspan": year_span if (k == i) else 0,

                    # estilos
                    "is_group_start": (i == 0 and k == i),
                    "is_year_start": (k == i),
                    "is_year_divider": (i != 0 and k == i),
                })

            i = j

    # ----------------------------
    # 6) data para selects de filtros
    # ----------------------------
    years = (
        Nomina.objects
        .values_list("Anio", flat=True)
        .distinct()
        .order_by("-Anio")
    )
    months = list(range(1, 13))
    form = NominaForm()
    return render(
        request,
        "Nomina/NominaIndex.html",
        {
            "nomina_rows": nomina_rows,
            "form": form,
            "years": years,
            "months": months,   # ✅ NUEVO
            "filters": filters,
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
    return render(request, 'Nomina/NominaForm.html', {'form': form})


@login_required
@verificar_permiso('can_manage_nomina')
@require_POST
def nomina_editar(request, id):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)

    nomina = get_object_or_404(Nomina, pk=id)

    salario = data.get('Salario')
    if salario is not None:
        try:
            nomina.Salario = parse_money_cop_to_decimal(salario)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

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


# (bulk_preview y bulk_create se quedan igual como los tienes)



# =========================================================
# BULK COPY (ORIGEN -> DESTINO) con preview editable
# =========================================================

@login_required
@verificar_permiso('can_manage_nomina')
@require_POST
def nomina_bulk_preview(request):
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
            'salario': format_cop_for_input(n.Salario),
            'cliente_id': n.Cliente_id,
        })

    return JsonResponse({'items': items, 'count': len(items)})


@login_required
@verificar_permiso('can_manage_nomina')
@require_POST
def nomina_bulk_create(request):
    try:
        data = json.loads(request.body)
        destino = data.get('destino', {})
        mode = (data.get('mode') or 'skip').lower()
        items = data.get('items') or []

        d_anio = int(str(destino.get('anio')).strip())
        raw_mes = destino.get('mes')
        d_months = parse_months_input(raw_mes)
    except Exception as e:
        return JsonResponse({'error': f'Payload inválido. {str(e)}'}, status=400)

    if mode not in ('skip', 'overwrite'):
        mode = 'skip'

    mes_field = Nomina._meta.get_field('Mes')
    mes_type = mes_field.get_internal_type()

    created = 0
    updated = 0
    skipped = 0
    errors = []

    with transaction.atomic():
        for idx, it in enumerate(items):
            try:
                empleado_id = int(it.get('empleado_id'))
                cliente_id = int(it.get('cliente_id'))
                salario_raw = it.get('salario', '')

                empleado = get_object_or_404(Empleado, pk=empleado_id)
                cliente = get_object_or_404(Clientes, pk=cliente_id)

                salario_dec = parse_money_cop_to_decimal(salario_raw)

                for d_mes_int in d_months:
                    d_mes_2 = f"{d_mes_int:02d}"
                    d_mes_1 = str(d_mes_int)
                    mes_for_save = d_mes_2 if mes_type in ("CharField", "TextField") else d_mes_int

                    base_qs = Nomina.objects.filter(Anio=d_anio, Documento_id=empleado_id)

                    if mes_type in ("CharField", "TextField"):
                        existing = base_qs.filter(Mes__in=[d_mes_2, d_mes_1]).first()
                    else:
                        existing = base_qs.filter(Mes=d_mes_int).first()

                    if existing:
                        if mode == 'overwrite':
                            existing.Salario = salario_dec
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
                        Salario=salario_dec,
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
        'dest_months': d_months,
    })
