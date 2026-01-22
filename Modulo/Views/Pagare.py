# Modulo/Views/Pagare.py
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils.dateparse import parse_date

from modulo.decorators import verificar_permiso
from modulo.forms import PagareFilterForm
from modulo.models import Empleado, Pagare, PagarePlaneado, PagareEjecutado, TipoPagare, ActividadPagare
from django.shortcuts import redirect
from django.contrib import messages


# ----------------------------
# Helpers robustos
# ----------------------------
def parse_decimal(v, default=Decimal("0")) -> Decimal:
    if v is None:
        return default
    if isinstance(v, (int, float, Decimal)):
        try:
            return Decimal(str(v))
        except InvalidOperation:
            return default
    s = str(v).strip()
    if s == "":
        return default

    # soporta "$ 1.234.567,89"
    s = (
        s.replace("$", "")
         .replace("\xa0", "")
         .replace(" ", "")
         .replace(".", "")
         .replace(",", ".")
    )
    try:
        return Decimal(s)
    except InvalidOperation:
        return default


def parse_int(v, default=0) -> int:
    try:
        if v is None or str(v).strip() == "":
            return default
        return int(float(str(v).strip()))
    except Exception:
        return default


def parse_date_or_none(v):
    if not v:
        return None
    if isinstance(v, str):
        d = parse_date(v[:10])
        return d
    return v


def json_error(msg: str, status=400):
    return JsonResponse({"success": False, "message": msg}, status=status)


def json_ok(message: str, extra: dict | None = None):
    payload = {"success": True, "message": message}
    if extra:
        payload.update(extra)
    return JsonResponse(payload, status=200)


# ----------------------------
# Views
# ----------------------------
@login_required
@verificar_permiso("can_manage_pagare")
def pagare_index(request):
    form = PagareFilterForm(request.GET or None)
    empleados = []

    actividades = ActividadPagare.objects.all()
    tipos_pagare = TipoPagare.objects.all()

    # esto alimenta el "pagares-data" oculto para el dropdown
    pagares = (
        Pagare.objects.select_related("Tipo_Pagare")
        .all()
        .only(
            "Pagare_Id",
            "Documento",
            "Tipo_Pagare__Desc_Tipo_Pagare",
            "Fecha_Creacion_Pagare",
            "estado",
        )
    )

    if form.is_valid():
        documentos = form.cleaned_data.get("documento")
        if documentos:
            empleados = (
                Empleado.objects.filter(Activo=True, Documento__in=documentos)
                .select_related("LineaId", "CargoId")
            )

    return render(
        request,
        'Pagare/Pagareindex.html',
        {
            "form": form,
            "empleados": empleados,
            "actividades": actividades,
            "tipos_pagare": tipos_pagare,
            "pagares": pagares,
        },
    )


@login_required
@verificar_permiso("can_manage_pagare")
@require_POST
def eliminar_pagares(request):
    try:
        data = json.loads(request.body or "{}")
        ids = data.get("ids", [])
        if not ids:
            return json_error("No se recibieron pagarés para eliminar.", 400)

        Pagare.objects.filter(Pagare_Id__in=ids).delete()
        return json_ok("Pagarés eliminados correctamente.")
    except Exception as e:
        return json_error(str(e), 500)


@login_required
@verificar_permiso("can_manage_pagare")
@require_POST
def obtener_datos_pagares(request):
    try:
        data = json.loads(request.body or "{}")
        ids = [parse_int(x) for x in data.get("pagare_ids", []) if parse_int(x) > 0]
        if not ids:
            return json_error("No se recibieron IDs válidos.", 400)

        pagares_qs = (
            Pagare.objects.select_related("Tipo_Pagare")
            .filter(Pagare_Id__in=ids)
        )

        # planeados
        planeados_qs = (
            PagarePlaneado.objects.select_related("Actividad", "Pagare")
            .filter(Pagare__Pagare_Id__in=ids)
        )

        # ejecutados
        ejecutados_qs = (
            PagareEjecutado.objects.select_related("Actividad", "Pagare")
            .filter(Pagare__Pagare_Id__in=ids)
        )

        pagares_data = []
        for p in pagares_qs:
            valor_pagare = parse_decimal(p.Valor_Pagare, Decimal("0"))
            ejec = parse_decimal(p.porcentaje_ejecucion, Decimal("0"))
            valor_cap = (valor_pagare * ejec) / Decimal("100") if valor_pagare and ejec else Decimal("0")

            pagares_data.append(
                {
                    "id": p.Pagare_Id,
                    "documento": p.Documento,
                    "fecha_creacion": p.Fecha_Creacion_Pagare.strftime("%Y-%m-%d"),
                    "tipo_pagare": {
                        "id": p.Tipo_Pagare.Tipo_PagareId,
                        "descripcion": p.Tipo_Pagare.Desc_Tipo_Pagare,
                    },
                    "descripcion": p.descripcion,
                    "fecha_inicio": p.Fecha_inicio_Condonacion.strftime("%Y-%m-%d") if p.Fecha_inicio_Condonacion else None,
                    "fecha_fin": p.Fecha_fin_Condonacion.strftime("%Y-%m-%d") if p.Fecha_fin_Condonacion else None,
                    "meses_condonacion": p.Meses_de_condonacion or 0,
                    "valor_pagare": str(valor_pagare),
                    "ejecucion": float(ejec),
                    "valor_capacitacion": float(valor_cap),
                    "estado": p.estado,
                }
            )

        planeados_data = [
            {
                "pagare_id": pl.Pagare.Pagare_Id,
                "actividad_id": pl.Actividad.Act_PagareId,
                "actividad_nombre": pl.Actividad.Descripcion_Act,
                "horas_planeadas": pl.Horas_Planeadas,
            }
            for pl in planeados_qs
        ]

        ejecutados_data = [
            {
                "pagare_id": ej.Pagare.Pagare_Id,
                "actividad_id": ej.Actividad.Act_PagareId,
                "actividad_nombre": ej.Actividad.Descripcion_Act,
                "horas_ejecutadas": ej.Horas_Ejecutadas,
            }
            for ej in ejecutados_qs
        ]

        return JsonResponse(
            {
                "pagares": pagares_data,
                "planeadas": planeados_data,
                "ejecutadas": ejecutados_data,
            },
            status=200,
        )
    except Exception as e:
        return json_error(str(e), 500)


@login_required
@verificar_permiso("can_manage_pagare")
@require_POST
def actualizar_pagare(request):
    """
    Espera: { "<doc>": { pagare_id, fecha_creacion, tipo_pagare, descripcion, ... , ejecutadas:[{actividad_id, horas}] } }
    """
    try:
        data = json.loads(request.body or "{}")
        if not isinstance(data, dict) or not data:
            return json_error("Payload inválido.", 400)

        with transaction.atomic():
            for doc, valores in data.items():
                pagare_id = parse_int(valores.get("pagare_id"))
                if pagare_id <= 0:
                    continue

                pagare = Pagare.objects.select_for_update().get(Pagare_Id=pagare_id)

                pagare.Fecha_Creacion_Pagare = parse_date_or_none(valores.get("fecha_creacion")) or pagare.Fecha_Creacion_Pagare
                pagare.Tipo_Pagare_id = parse_int(valores.get("tipo_pagare"), pagare.Tipo_Pagare_id)
                pagare.descripcion = (valores.get("descripcion") or "").strip() or pagare.descripcion

                pagare.Fecha_inicio_Condonacion = parse_date_or_none(valores.get("fecha_inicio"))
                pagare.Fecha_fin_Condonacion = parse_date_or_none(valores.get("fecha_fin")) if pagare.Fecha_inicio_Condonacion else None

                pagare.Meses_de_condonacion = parse_int(valores.get("meses_condonacion"), pagare.Meses_de_condonacion or 0)
                pagare.Valor_Pagare = parse_decimal(valores.get("valor_pagare"), parse_decimal(pagare.Valor_Pagare))
                pagare.porcentaje_ejecucion = parse_decimal(valores.get("ejecucion"), parse_decimal(pagare.porcentaje_ejecucion))
                pagare.estado = valores.get("estado") or pagare.estado

                # Si en tu DB existe columna Valor_Capacitacion, esto lo permite sin romper si no existe:
                if hasattr(pagare, "Valor_Capacitacion"):
                    setattr(pagare, "Valor_Capacitacion", parse_decimal(valores.get("valor_capacitacion")))

                pagare.save()

                # Ejecutadas (upsert + delete missing)
                recibidas = valores.get("ejecutadas", []) or []
                recibidas_ids = []
                for act in recibidas:
                    actividad_id = parse_int(act.get("actividad_id"))
                    if actividad_id <= 0:
                        continue
                    recibidas_ids.append(actividad_id)

                    PagareEjecutado.objects.update_or_create(
                        Pagare=pagare,
                        Actividad_id=actividad_id,
                        defaults={"Horas_Ejecutadas": parse_int(act.get("horas"), 0)},
                    )

                PagareEjecutado.objects.filter(Pagare=pagare).exclude(Actividad_id__in=recibidas_ids).delete()

        return JsonResponse({"mensaje": "Actualización exitosa"}, status=200)

    except Pagare.DoesNotExist:
        return json_error("Uno de los pagarés no existe.", 404)
    except Exception as e:
        return json_error(str(e), 500)


@login_required
@verificar_permiso("can_manage_pagare")
@require_POST
def guardar_pagare(request):
    """
    Espera JSON (lista):
    [
      { documento, general:{...}, planeado:[...], ejecutado:[...] },
      ...
    ]
    """
    try:
        if request.content_type != "Application/Json":
            return json_error("Se esperaba JSON.", 400)

        payload = json.loads(request.body or "[]")
        if not isinstance(payload, list) or not payload:
            return json_error("Payload inválido.", 400)

        with transaction.atomic():
            for item in payload:
                doc = (item.get("documento") or "").strip()
                general = item.get("general") or {}
                if not doc:
                    continue

                ejecucion_raw = general.get("ejecucion", None)
                ejecucion = parse_decimal(str(ejecucion_raw).replace("%", "") if ejecucion_raw else None, Decimal("0"))

                pagare = Pagare.objects.create(
                    Documento=doc,
                    Fecha_Creacion_Pagare=parse_date_or_none(general.get("fecha_creacion")) or None,
                    Tipo_Pagare_id=parse_int(general.get("tipo_pagare")),
                    descripcion=(general.get("descripcion") or "Sin descripción").strip(),
                    Fecha_inicio_Condonacion=parse_date_or_none(general.get("fecha_inicio")),
                    Fecha_fin_Condonacion=parse_date_or_none(general.get("fecha_fin")),
                    Meses_de_condonacion=parse_int(general.get("meses_condonacion")),
                    Valor_Pagare=parse_decimal(general.get("valor_pagare")),
                    porcentaje_ejecucion=ejecucion,
                    estado=general.get("estado") or "Proceso",
                )

                for pl in item.get("planeado", []) or []:
                    PagarePlaneado.objects.update_or_create(
                        Pagare=pagare,
                        Actividad_id=parse_int(pl.get("actividad_id")),
                        defaults={"Horas_Planeadas": parse_int(pl.get("horas"), 0)},
                    )

                for ej in item.get("ejecutado", []) or []:
                    PagareEjecutado.objects.update_or_create(
                        Pagare=pagare,
                        Actividad_id=parse_int(ej.get("actividad_id")),
                        defaults={"Horas_Ejecutadas": parse_int(ej.get("horas"), 0)},
                    )

        return JsonResponse({"estado": "exito", "mensaje": "Datos guardados correctamente (JSON)"}, status=200)

    except Exception as e:
        return json_error(str(e), 500)

@login_required
@verificar_permiso("can_manage_pagare")
def obtener_pagares_empleado(request):
    """
    Devuelve pagarés por documento de empleado.
    GET: /obtener_pagares/?documento=123
    POST (opcional): { "documento": "123" }
    """
    try:
        documento = (request.GET.get("documento") or "").strip()

        if not documento and request.method == "POST":
            data = json.loads(request.body or "{}")
            documento = str(data.get("documento") or "").strip()

        if not documento:
            return json_error("Falta parámetro 'documento'.", 400)

        qs = (
            Pagare.objects.select_related("Tipo_Pagare")
            .filter(Documento=documento)
            .only("Pagare_Id", "Documento", "Fecha_Creacion_Pagare", "estado", "Tipo_Pagare__Desc_Tipo_Pagare")
            .order_by("-Fecha_Creacion_Pagare")
        )

        pagares = []
        for p in qs:
            pagares.append({
                "id": p.Pagare_Id,
                "documento": p.Documento,
                "tipo": getattr(p.Tipo_Pagare, "Desc_Tipo_Pagare", "") if p.Tipo_Pagare_id else "",
                "fecha_creacion": p.Fecha_Creacion_Pagare.strftime("%Y-%m-%d") if p.Fecha_Creacion_Pagare else None,
                "estado": p.estado,
            })

        return JsonResponse({"success": True, "pagares": pagares}, status=200)

    except Exception as e:
        return json_error(str(e), 500)


@login_required
@verificar_permiso("can_manage_pagare")
def pag_planeado(request, pagare_id: int):
    """
    Pantalla y guardado del planeado.
    Nota: como tus checkboxes NO tienen name, el backend toma como seleccionadas
    las actividades que vengan como inputs horas_planeadas_<id>.
    """
    pagare = get_object_or_404(Pagare, Pagare_Id=pagare_id)
    todas_actividades = ActividadPagare.objects.all()

    if request.method == "POST":
        try:
            actividad_ids = []
            for k, v in request.POST.items():
                if not k.startswith("horas_planeadas_"):
                    continue
                act_id = parse_int(k.replace("horas_planeadas_", ""))
                if act_id <= 0:
                    continue
                actividad_ids.append(act_id)

                PagarePlaneado.objects.update_or_create(
                    Pagare=pagare,
                    Actividad_id=act_id,
                    defaults={"Horas_Planeadas": parse_int(v, 0)},
                )

            # si no vino ninguna, borra todas (depende del comportamiento que quieras)
            PagarePlaneado.objects.filter(Pagare=pagare).exclude(Actividad_id__in=actividad_ids).delete()

            messages.success(request, "Pagaré planeado actualizado correctamente.")
            return redirect("pag_planeado", pagare_id=pagare_id)

        except Exception as e:
            messages.error(request, f"Error guardando planeado: {e}")

    return render(
        request,
        'Pagare/Pagplaneado.html',
        {
            "pagare": pagare,
            "todas_actividades": todas_actividades,
        },
    )


@login_required
@verificar_permiso("can_manage_pagare")
def pag_ejecutado(request, pagare_id: int):
    """
    Pantalla y guardado del ejecutado.
    Igual que planeado: detecta por inputs horas_ejecutadas_<id>.
    """
    pagare = get_object_or_404(Pagare, Pagare_Id=pagare_id)
    todas_actividades = ActividadPagare.objects.all()

    if request.method == "POST":
        try:
            actividad_ids = []
            for k, v in request.POST.items():
                if not k.startswith("horas_ejecutadas_"):
                    continue
                act_id = parse_int(k.replace("horas_ejecutadas_", ""))
                if act_id <= 0:
                    continue
                actividad_ids.append(act_id)

                PagareEjecutado.objects.update_or_create(
                    Pagare=pagare,
                    Actividad_id=act_id,
                    defaults={"Horas_Ejecutadas": parse_int(v, 0)},
                )

            PagareEjecutado.objects.filter(Pagare=pagare).exclude(Actividad_id__in=actividad_ids).delete()

            messages.success(request, "Pagaré ejecutado actualizado correctamente.")
            return redirect("pag_ejecutado", pagare_id=pagare_id)

        except Exception as e:
            messages.error(request, f"Error guardando ejecutado: {e}")

    return render(
        request,
        'Pagare/Pagejecutado.html',
        {
            "pagare": pagare,
            "todas_actividades": todas_actividades,
        },
    )

