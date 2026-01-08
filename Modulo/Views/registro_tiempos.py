from decimal import Decimal
import json
from collections import defaultdict

from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from django.contrib.auth.decorators import login_required

from Modulo.forms import ColaboradorFilterForm
from Modulo.models import (
    Clientes, Concepto, Consultores, Empleado, Horas_Habiles,
    Ind_Operat_Clientes, Ind_Operat_Conceptos, Linea, Modulo,
    Tiempos_Cliente, TiemposConcepto, TiemposFacturables
)
from Modulo.decorators import verificar_permiso


# -------------------------
# Helpers (SIN decoradores)
# -------------------------
def guardar_tiempos_cliente(anio, mes, documento, cliente_id, linea_id, modulo_id, horas):
    try:
        if not modulo_id:
            raise ValidationError("El campo ModuloId es requerido.")
        if not str(modulo_id).isdigit():
            raise ValidationError("ModuloId debe ser un número entero válido.")
        modulo_id = int(modulo_id)

        tiempo_cliente, creado = Tiempos_Cliente.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            Documento=documento,
            ClienteId_id=cliente_id,
            LineaId_id=linea_id,
            ModuloId_id=modulo_id,
            defaults={'Horas': horas}
        )
        if creado:
            if horas == '0':
                tiempo_cliente.delete()
        else:
            if horas == '0':
                tiempo_cliente.delete()
            elif tiempo_cliente.Horas != horas:
                tiempo_cliente.Horas = horas
                tiempo_cliente.save()
        return tiempo_cliente
    except Exception as e:
        raise ValidationError(f"Error al guardar los tiempos del cliente: {str(e)}")


def guardar_tiempos_concepto(anio, mes, documento, concepto_id, linea_id, horas):
    try:
        tiempo_concepto, creado = TiemposConcepto.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            Documento=documento,
            defaults={'Horas': horas},
            ConceptoId_id=concepto_id,
            LineaId_id=linea_id
        )
        if creado:
            if horas == '0':
                tiempo_concepto.delete()
        else:
            if horas == '0':
                tiempo_concepto.delete()
            elif tiempo_concepto.Horas != horas:
                tiempo_concepto.Horas = horas
                tiempo_concepto.save()
        return tiempo_concepto
    except Exception as e:
        raise ValidationError(f"Error al guardar los tiempos del concepto: {str(e)}")


def guardar_tiempos_facturables(anio, mes, linea_id, cliente_id, horas):
    try:
        tiempo_facturable, creado = TiemposFacturables.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            LineaId_id=linea_id,
            ClienteId_id=cliente_id,
            defaults={'Horas': horas}
        )
        if creado:
            if horas == '0':
                tiempo_facturable.delete()
        else:
            if horas == '0':
                tiempo_facturable.delete()
            elif tiempo_facturable.Horas != horas:
                tiempo_facturable.Horas = horas
                tiempo_facturable.save()
        return tiempo_facturable
    except Exception as e:
        raise ValidationError(f"Error al guardar los tiempos facturables: {str(e)}")


def guardar_totales_operacion(anio, mes, linea_id, horas_trabajadas, horas_facturables):
    try:
        anio = int(anio)
        mes = int(mes)
        linea_id = int(linea_id)
        horas_trabajadas = float(horas_trabajadas)
        horas_facturables = float(horas_facturables)
        linea = Linea.objects.get(LineaId=linea_id)
        total_operacion, creado = Ind_Operat_Clientes.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            LineaId=linea,
            defaults={'HorasTrabajadas': horas_trabajadas, 'HorasFacturables': horas_facturables}
        )
        if not creado:
            total_operacion.HorasTrabajadas = horas_trabajadas
            total_operacion.HorasFacturables = horas_facturables
            total_operacion.save()
        return total_operacion
    except Exception as e:
        raise ValidationError(f"Error al guardar los totales de operación: {str(e)}")


def guardar_totales_concepto(anio, mes, linea_id, concepto_id, horas_concepto):
    try:
        anio = int(anio)
        mes = int(mes)
        linea_id = int(linea_id)
        concepto_id = int(concepto_id)
        horas_concepto = float(horas_concepto)
        linea = Linea.objects.get(LineaId=linea_id)
        concepto = Concepto.objects.get(ConceptoId=concepto_id)
        total_concepto, creado = Ind_Operat_Conceptos.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            LineaId=linea,
            ConceptoId=concepto,
            defaults={'HorasConcepto': horas_concepto}
        )
        if not creado:
            total_concepto.HorasConcepto = horas_concepto
            total_concepto.save()
        return total_concepto
    except Exception as e:
        raise ValidationError(f"Error al guardar los totales por concepto: {str(e)}")


# Índices en memoria para evitar N+1 queries en la tabla grande
def build_tiempo_clientes_index(qs):
    """
    index[Documento][ModuloId][LineaId][ClienteId] = horas
    """
    index = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(float)
            )
        )
    )
    for t in qs:
        doc = t.Documento
        mod = int(t.ModuloId_id)
        linea = int(t.LineaId_id)
        cliente = int(t.ClienteId_id)
        index[doc][mod][linea][cliente] += float(t.Horas)
    return index


def build_tiempo_conceptos_index(qs):
    """
    index[Documento][LineaId][ConceptoId] = horas
    """
    index = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for t in qs:
        doc = t.Documento
        linea = int(t.LineaId_id)
        concepto = int(t.ConceptoId_id)
        index[doc][linea][concepto] += float(t.Horas)
    return index


def build_tiempos_facturables_index(qs):
    """
    index[LineaId][ClienteId] = horas
    """
    index = defaultdict(lambda: defaultdict(float))
    for t in qs:
        linea = int(t.LineaId_id)
        cliente = int(t.ClienteId_id)
        index[linea][cliente] += float(t.Horas)
    return index


# -------------------------
# Views (CON decoradores)
# -------------------------
@login_required
@verificar_permiso('can_manage_registro_tiempos')
@transaction.atomic
def registro_tiempos_guardar(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rows = data.get('data', [])
            for row in rows:
                if 'Documento' in row:
                    documento = row.get('Documento')
                    anio = row.get('Anio')
                    mes = row.get('Mes')
                    linea_id = row.get('LineaId')
                    modulo_id = row.get('ModuloId')

                    if 'ClienteId' in row and 'Tiempo_Clientes' in row:
                        guardar_tiempos_cliente(
                            anio,
                            mes,
                            documento,
                            row.get('ClienteId'),
                            linea_id,
                            modulo_id,
                            row.get('Tiempo_Clientes')
                        )
                    elif 'ConceptoId' in row and 'Tiempo_Conceptos' in row:
                        guardar_tiempos_concepto(
                            anio,
                            mes,
                            documento,
                            row.get('ConceptoId'),
                            linea_id,
                            row.get('Tiempo_Conceptos')
                        )

                elif 'LineaId' in row and 'Horas_Facturables' in row and 'ClienteId' in row:
                    guardar_tiempos_facturables(
                        anio=row.get('Anio'),
                        mes=row.get('Mes'),
                        linea_id=row.get('LineaId'),
                        cliente_id=row.get('ClienteId'),
                        horas=row.get('Horas_Facturables')
                    )

                elif 'type' in row:
                    if row['type'] == 'linea':
                        guardar_totales_operacion(
                            anio=row.get('Anio'),
                            mes=row.get('Mes'),
                            linea_id=row.get('LineaId'),
                            horas_trabajadas=row.get('horasTrabajadas'),
                            horas_facturables=row.get('horasFacturables')
                        )
                    elif row['type'] == 'concepto':
                        guardar_totales_concepto(
                            anio=row.get('Anio'),
                            mes=row.get('Mes'),
                            linea_id=row.get('LineaId'),
                            concepto_id=row.get('ConceptoId'),
                            horas_concepto=row.get('horas')
                        )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})
    return JsonResponse({'status': 'error', 'error': 'Método no permitido.'})


@login_required
@verificar_permiso('can_manage_registro_tiempos')
def registro_tiempos_index(request):
    colaborador_info = []
    lineas_info = []
    show_data = False

    # Formularios de filtro
    form = ColaboradorFilterForm(request.GET or None)

    # Base de catálogos (ligeros)
    clientes_qs = Clientes.objects.all().order_by('Nombre_Cliente').only('ClienteId', 'Nombre_Cliente')
    conceptos_qs = Concepto.objects.all()

    # Estos se sobreescribirán si hay datos
    clientes_visibles = clientes_qs.none()
    conceptos_visibles = conceptos_qs

    if request.method == 'GET' and 'buscar' in request.GET and form.is_valid():
        # Querysets base para el período / filtros
        empleados = Empleado.objects.select_related('LineaId', 'PerfilId', 'ModuloId').all().order_by('Documento')
        consultores = Consultores.objects.select_related('LineaId', 'PerfilId', 'ModuloId').all().order_by('Documento')
        tiempo_clientes = Tiempos_Cliente.objects.select_related('ClienteId', 'LineaId', 'ModuloId').all()
        tiempo_conceptos = TiemposConcepto.objects.select_related('ConceptoId', 'LineaId').all()
        horas_facturables = TiemposFacturables.objects.select_related('LineaId', 'ClienteId').all()
        lineas = Linea.objects.all()

        # Filtrar por año/mes/línea/empleado/consultor/cliente
        empleados, consultores, tiempo_clientes, tiempo_conceptos = filtrar_colaboradores(
            form, empleados, consultores, clientes_qs, tiempo_clientes, tiempo_conceptos
        )

        # Filtrar clientes visibles según el filtro de cliente
        clientes_visibles = clientes_qs
        cliente_obj = form.cleaned_data.get('ClienteId')
        if cliente_obj:
            cliente_pk = getattr(cliente_obj, "pk", cliente_obj)
            clientes_visibles = clientes_visibles.filter(ClienteId=cliente_pk)

        # Reducir tiempos únicamente a los documentos filtrados (empleados + consultores)
        documentos_empleados = list(empleados.values_list('Documento', flat=True))
        documentos_consultores = list(consultores.values_list('Documento', flat=True))
        documentos = documentos_empleados + documentos_consultores

        if documentos:
            tiempo_clientes = tiempo_clientes.filter(Documento__in=documentos)
            tiempo_conceptos = tiempo_conceptos.filter(Documento__in=documentos)

        # Construir índices en memoria para evitar N+1 queries
        tiempos_clientes_idx = build_tiempo_clientes_index(tiempo_clientes)
        tiempos_conceptos_idx = build_tiempo_conceptos_index(tiempo_conceptos)

        # Empleados
        for empleado in empleados:
            info = obtener_info_colaborador(
                empleado,
                clientes_visibles,
                conceptos_qs,
                tiempos_clientes_idx,
                tiempos_conceptos_idx
            )
            if info:
                colaborador_info.append(info)

        # Consultores (pueden tener varios módulos)
        for consultor in consultores:
            modulos_tarifa = Modulo.objects.filter(
                tarifa_consultores__documentoId=consultor.Documento
            ).distinct()
            modulos_tiempos = Modulo.objects.filter(
                tiempos_cliente__Documento=consultor.Documento
            ).distinct()
            modulos = (modulos_tarifa | modulos_tiempos).distinct()

            if modulos.exists():
                for modulo in modulos:
                    info = obtener_info_colaborador(
                        consultor,
                        clientes_visibles,
                        conceptos_qs,
                        tiempos_clientes_idx,
                        tiempos_conceptos_idx,
                        modulo
                    )
                    if info:
                        colaborador_info.append(info)
            else:
                info = obtener_info_colaborador(
                    consultor,
                    clientes_visibles,
                    conceptos_qs,
                    tiempos_clientes_idx,
                    tiempos_conceptos_idx
                )
                if info:
                    colaborador_info.append(info)

        # Ordenar por Nombre y Empresa
        colaborador_info = sorted(
            colaborador_info,
            key=lambda x: (x.get('Nombre', ''), x.get('Empresa', ''))
        )
        show_data = bool(colaborador_info)

        # Tiempo facturable por línea
        lineas_unicas = list({c['Linea'] for c in colaborador_info})
        tiempos_facturables, lineas, clientes_visibles = filtrar_linea(
            form, horas_facturables, lineas, clientes_visibles
        )

        if lineas_unicas:
            tiempos_facturables_idx = build_tiempos_facturables_index(tiempos_facturables)
            for linea in lineas:
                if linea.Linea in lineas_unicas:
                    lineas_info.append(
                        obtener_info_linea(linea, clientes_visibles, tiempos_facturables_idx)
                    )
    else:
        # No se ha hecho búsqueda aún o el formulario no es válido
        horas_facturables = TiemposFacturables.objects.none()

    totales, totales_facturables = calcular_totales(colaborador_info, lineas_info)

    context = {
        'form': form,
        'colaborador_info': colaborador_info,
        'Clientes': clientes_visibles.only('ClienteId', 'Nombre_Cliente') if show_data else clientes_qs.none(),
        'Conceptos': conceptos_qs,
        'Totales': totales,
        'TotalesFacturables': totales_facturables,
        'Horas_Facturables': horas_facturables,
        'Tiempo_Lineas': lineas_info,
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if (not colaborador_info and 'buscar' in request.GET) else ""
    }
    return render(request, 'Registro_Tiempos/registro_tiempos_index.html', context)


def filtrar_colaboradores(form, empleados, consultores, clientes, tiempo_clientes, tiempo_conceptos):
    empleados = empleados.order_by('Documento')
    consultores = consultores.order_by('Documento')

    anio = form.cleaned_data.get('Anio')
    mes = form.cleaned_data.get('Mes')
    linea = form.cleaned_data.get('LineaId')
    empleado = form.cleaned_data.get('Empleado')
    consultor = form.cleaned_data.get('Consultor')
    cliente = form.cleaned_data.get('ClienteId')

    if anio:
        tiempo_clientes = tiempo_clientes.filter(Anio=anio)
        tiempo_conceptos = tiempo_conceptos.filter(Anio=anio)
    if mes:
        tiempo_clientes = tiempo_clientes.filter(Mes=mes)
        tiempo_conceptos = tiempo_conceptos.filter(Mes=mes)
    if linea:
        empleados = empleados.filter(LineaId=linea)
        consultores = consultores.filter(LineaId=linea)
    if empleado:
        empleados = empleados.filter(Documento=empleado)
    if consultor:
        consultores = consultores.filter(Documento=consultor)
    if cliente:
        tiempo_clientes = tiempo_clientes.filter(ClienteId=cliente)

    return empleados, consultores, tiempo_clientes, tiempo_conceptos


def filtrar_linea(form, tiempos_facturables, lineas, clientes):
    tiempos_facturables = tiempos_facturables.order_by('LineaId')
    anio = form.cleaned_data.get('Anio')
    mes = form.cleaned_data.get('Mes')
    linea_id = form.cleaned_data.get('LineaId')
    cliente_sel = form.cleaned_data.get('ClienteId')

    if anio:
        tiempos_facturables = tiempos_facturables.filter(Anio=anio)
    if mes:
        tiempos_facturables = tiempos_facturables.filter(Mes=mes)
    if linea_id:
        tiempos_facturables = tiempos_facturables.filter(LineaId=linea_id)

    if cliente_sel:
        cliente_pk = getattr(cliente_sel, "pk", cliente_sel)
        tiempos_facturables = tiempos_facturables.filter(ClienteId_id=cliente_pk)
        clientes = clientes.filter(ClienteId=cliente_pk)

    return tiempos_facturables, lineas, clientes


def obtener_info_colaborador(colaborador, clientes, conceptos, tiempo_clientes_idx, tiempo_conceptos_idx, modulo=None):
    cliente_info = {c.ClienteId: c for c in clientes}
    concepto_info = {c.ConceptoId: c for c in conceptos}

    if modulo:
        modulo_id = int(modulo.ModuloId)
        modulo_nombre = modulo.Modulo
    else:
        modulo_id = int(colaborador.ModuloId_id)
        modulo_nombre = colaborador.ModuloId.Modulo

    linea_id = int(colaborador.LineaId_id)

    # Horas por cliente desde índice en memoria
    clientes_colaborador = {c.ClienteId: 0 for c in clientes}
    horas_cliente_map = (
        tiempo_clientes_idx
            .get(colaborador.Documento, {})
            .get(modulo_id, {})
            .get(linea_id, {})
    )
    for cid in clientes_colaborador:
        if cid in horas_cliente_map:
            clientes_colaborador[cid] = float(horas_cliente_map[cid])

    total_horas_clientes = sum(clientes_colaborador.values())

    # Horas por concepto desde índice en memoria
    conceptos_colaborador = {c.ConceptoId: 0 for c in conceptos}
    horas_conceptos_map = (
        tiempo_conceptos_idx
            .get(colaborador.Documento, {})
            .get(linea_id, {})
    )
    for ccid in conceptos_colaborador:
        if ccid in horas_conceptos_map:
            conceptos_colaborador[ccid] = float(horas_conceptos_map[ccid])

    total_horas_conceptos = sum(conceptos_colaborador.values())
    total_horas_trabajadas = total_horas_clientes + total_horas_conceptos
    tiene_horas = total_horas_trabajadas > 0

    activo_flag = (colaborador.Activo if isinstance(colaborador, Empleado) else colaborador.Estado)

    if activo_flag or tiene_horas:
        return {
            'Nombre': colaborador.Nombre,
            'Documento': colaborador.Documento,
            'Linea': colaborador.LineaId.Linea,
            'LineaId': linea_id,
            'Perfil': colaborador.PerfilId.Perfil,
            'ModuloId': modulo_id,
            'Modulo': modulo_nombre,
            'Empresa': "Flag Soluciones" if isinstance(colaborador, Empleado) else colaborador.Empresa,
            'Clientes': {
                cid: {
                    'Cliente': cliente_info[cid].Nombre_Cliente,
                    'ClienteId': cid,
                    'tiempo_clientes': horas
                }
                for cid, horas in clientes_colaborador.items()
            },
            'Total_Clientes': total_horas_clientes,
            'Conceptos': {
                ccid: {
                    'Concepto': concepto_info[ccid].Descripcion,
                    'ConceptoId': ccid,
                    'tiempo_conceptos': horas
                }
                for ccid, horas in conceptos_colaborador.items()
            },
            'Total_Conceptos': total_horas_conceptos,
            'Total_Horas': total_horas_trabajadas,
            'Activo': activo_flag,
        }
    return None


def obtener_info_linea(linea, clientes, tiempo_facturables_idx):
    cliente_info = {c.ClienteId: c for c in clientes}
    clientes_linea = {c.ClienteId: 0 for c in clientes}

    horas_linea_map = tiempo_facturables_idx.get(linea.LineaId, {})

    for cid in clientes_linea:
        if cid in horas_linea_map:
            clientes_linea[cid] = float(horas_linea_map[cid])

    total_horas_facturables = sum(clientes_linea.values())

    return {
        'Linea': linea.Linea,
        'LineaId': linea.LineaId,
        'Clientes': {
            cid: {
                'Cliente': cliente_info[cid].Nombre_Cliente,
                'ClienteId': cid,
                'horas_facturables': horas
            }
            for cid, horas in clientes_linea.items()
        },
        'Total_Horas_Facturables': total_horas_facturables
    }


def calcular_totales(colaborador_info, lineas_info):
    totales = defaultdict(Decimal)
    totales_facturables = defaultdict(Decimal)

    for empleado in colaborador_info:
        for cliente in empleado['Clientes'].values():
            totales[cliente['ClienteId']] += Decimal(str(cliente['tiempo_clientes']))
        for concepto in empleado['Conceptos'].values():
            totales[concepto['ConceptoId']] += Decimal(str(concepto['tiempo_conceptos']))

    totales['Total_Clientes'] = sum(Decimal(str(e['Total_Clientes'])) for e in colaborador_info) if colaborador_info else Decimal('0')
    totales['Total_Conceptos'] = sum(Decimal(str(e['Total_Conceptos'])) for e in colaborador_info) if colaborador_info else Decimal('0')
    totales['Total_Horas'] = sum(Decimal(str(e['Total_Horas'])) for e in colaborador_info) if colaborador_info else Decimal('0')

    for linea in lineas_info:
        for cliente in linea['Clientes'].values():
            totales_facturables[cliente['ClienteId']] += Decimal(str(cliente['horas_facturables']))

    totales_facturables['Total_Clientes'] = sum(
        Decimal(str(l['Total_Horas_Facturables']))
        for l in lineas_info
    ) if lineas_info else Decimal('0')
    totales_facturables['Total_Horas'] = totales_facturables['Total_Clientes']

    return totales, totales_facturables


def obtener_horas_habiles(anio, mes):
    try:
        horas_habiles = Horas_Habiles.objects.get(Anio=anio, Mes=mes)
        return horas_habiles.Dias_Habiles, horas_habiles.Horas_Laborales
    except Horas_Habiles.DoesNotExist:
        return None, None


@login_required
@verificar_permiso('can_manage_registro_tiempos')
def obtener_horas_habiles_view(request):
    anio = request.GET.get('anio')
    mes = request.GET.get('mes')
    dias_habiles, horas_laborales = obtener_horas_habiles(anio, mes)
    return JsonResponse({'Dias_Habiles': dias_habiles, 'Horas_Laborales': horas_laborales})


def calcular_totales_por_linea(datos):
    totales_operacion = defaultdict(float)
    totales_facturables = defaultdict(float)
    totales_conceptos = defaultdict(lambda: defaultdict(float))

    for fila in datos:
        linea = fila['Línea']
        total_operacion = float(fila['Total Operación'])
        horas_facturables = float(fila.get('Horas Facturables', 0))
        totales_operacion[linea] += total_operacion
        totales_facturables[linea] += horas_facturables
        for concepto, horas in fila.items():
            if concepto in ['Líder', 'Capacitaciones', 'Día Familia', 'Vacaciones', 'Calamidad', 'Preventa', 'Otros']:
                totales_conceptos[linea][concepto] += float(horas)

    return totales_operacion, totales_facturables, totales_conceptos
