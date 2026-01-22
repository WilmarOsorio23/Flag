from collections import defaultdict
from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from modulo.forms import Ind_Totales_FilterForm
from modulo.models import Clientes, Linea, FacturacionClientes, Tiempos_Cliente, Horas_Habiles, Nomina, Tarifa_Consultores, Tarifa_Clientes, IPC
from django.db.models import Sum
import json
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

def obtener_horas_habiles(anio: str) -> dict:
    """Obtiene días y horas hábiles por mes para un año específico"""
    registros = Horas_Habiles.objects.filter(Anio=anio)
    return {
        str(r.Mes): {
            'dias': r.Dias_Habiles,
            'horas_mes': r.Dias_Habiles * r.Horas_Laborales,
            'horas_diarias': r.Horas_Laborales
        } for r in registros
    }

def precargar_datos(anio: str, meses: list, clientes: list, lineas: list):
    """Precarga todos los datos necesarios para optimizar consultas"""
    clientes_ids = [c.ClienteId for c in clientes]
    lineas_ids = [l.LineaId for l in lineas]
    
    # Precargar tiempos
    tiempos = Tiempos_Cliente.objects.filter(
        Anio=anio,
        Mes__in=meses,
        ClienteId__in=clientes_ids,
        LineaId__in=lineas_ids
    ).values('Anio', 'Mes', 'Documento', 'ClienteId', 'LineaId', 'Horas', 'ModuloId')
    
    # Precargar facturación
    facturacion = FacturacionClientes.objects.filter(
        Anio=anio,
        Mes__in=meses
    ).values('ClienteId', 'LineaId', 'Mes', 'HorasFactura', 'DiasFactura', 'MesFactura', 'Valor')
    
    # Precargar nóminas
    nominas = Nomina.objects.all().values('Documento', 'Anio', 'Mes', 'Salario')
    nominas_dict = defaultdict(list)
    for n in nominas:
        nominas_dict[n['Documento']].append((int(n['Anio']), int(n['Mes']), Decimal(str(n['Salario'] or '0'))))
    
    # Ordenar nominas
    for doc in nominas_dict:
        nominas_dict[doc].sort(key=lambda x: (-x[0], -x[1]))
    
    # Precargar tarifas consultores
    tarifas_consultores = Tarifa_Consultores.objects.all().values(
        'documentoId', 'anio', 'mes', 'valorHora', 'valorDia', 'valorMes', 'moduloId'
    )
    tarifas_consultores_dict = defaultdict(lambda: defaultdict(list))
    for t in tarifas_consultores:
        tarifas_consultores_dict[t['documentoId']][t['moduloId']].append((
            int(t['anio']), 
            int(t['mes']),
            Decimal(str(t['valorHora'] or '0')),
            Decimal(str(t['valorDia'] or '0')),
            Decimal(str(t['valorMes'] or '0'))
        ))
    
    # Ordenar tarifas consultores
    for doc in tarifas_consultores_dict:
        for modulo in tarifas_consultores_dict[doc]:
            tarifas_consultores_dict[doc][modulo].sort(key=lambda x: (-x[0], -x[1]))
    
    # Precargar tarifas clientes
    tarifas_clientes = Tarifa_Clientes.objects.filter(clienteId__in=clientes_ids)
    tarifas_por_cliente = defaultdict(list)
    for tarifa in tarifas_clientes:
        tarifas_por_cliente[tarifa.clienteId_id].append(tarifa)
    
    return {
        'tiempos_data': list(tiempos),
        'facturacion_data': facturacion,
        'nominas_dict': nominas_dict,
        'tarifas_consultores_dict': tarifas_consultores_dict,
        'tarifas_por_cliente': tarifas_por_cliente
    }

def calcular_trabajado(cliente_id: str, anio: str, mes: str, lineas_ids: list, tiempos_data: list) -> Decimal:
    """Calcula horas trabajadas usando datos precargados"""
    return sum(
        t['Horas'] for t in tiempos_data 
        if t['ClienteId'] == cliente_id
        and str(t['Anio']) == anio 
        and str(t['Mes']) == mes 
        and t['LineaId'] in lineas_ids
    )

def calcular_costo(cliente_id: str, mes: str, lineas_ids: list, tiempos_data: list, hh_mes: dict, nominas_dict: dict, tarifas_consultores_dict: dict) -> Decimal:
    total = Decimal('0.00')
    mes_int = int(mes)
    
    for tiempo in tiempos_data:
        if tiempo['ClienteId'] != cliente_id or str(tiempo['Mes']) != mes or tiempo['LineaId'] not in lineas_ids:
            continue

        documento = tiempo['Documento']
        anio_int = int(tiempo['Anio'])
        modulo_id = tiempo['ModuloId']
        costo_hora = Decimal('0.00')
        
        # Lógica para empleados
        if documento in nominas_dict:
            entradas_nomina = nominas_dict[documento]
            entrada = next((e for e in entradas_nomina if e[0] <= anio_int and e[1] <= mes_int), None)
            if entrada:
                salario = entrada[2]
                ipc = obtener_ipc_anio(anio_int)
                salario_ajustado = salario * Decimal(str(ipc))
                horas_mes_total = hh_mes.get('horas_mes', Decimal('1'))
                costo_hora = salario_ajustado / horas_mes_total if horas_mes_total else Decimal('0')
        
        # Lógica para consultores
        else:
            entradas_tarifa = tarifas_consultores_dict[documento].get(modulo_id, [])
            entrada = next((e for e in entradas_tarifa if e[0] <= anio_int and e[1] <= mes_int), None)
            if entrada:
                valorHora, valorDia, valorMes = entrada[2], entrada[3], entrada[4]
                horas_diarias = hh_mes.get('horas_diarias', Decimal('1'))
                horas_mes_total = hh_mes.get('horas_mes', Decimal('1'))
                
                if valorHora > 0:
                    costo_hora = valorHora
                elif valorDia > 0:
                    costo_hora = valorDia / horas_diarias
                elif valorMes > 0:
                    costo_hora = valorMes / horas_mes_total

        total += Decimal(tiempo['Horas']) * costo_hora
    
    return total

def calcular_facturado(anio: str, mes: str, cliente: Clientes, lineas_ids: list, facturacion_data: dict, horas_habiles: dict) -> dict:
    """Calcula facturación usando datos precargados"""
    total_valor = Decimal('0.00')
    total_horas = Decimal('0.00')  # Nuevo: horas facturadas
    hh = horas_habiles.get(mes, {})
    
    for f in facturacion_data:
        if f['ClienteId'] == cliente.ClienteId and str(f['Mes']) == mes and f['LineaId'] in lineas_ids:
            horas = Decimal('0.00')
            
            if f['HorasFactura']: 
                horas += Decimal(str(f['HorasFactura']))
            elif f['DiasFactura']: 
                horas += Decimal(str(f['DiasFactura'])) * hh.get('horas_diarias', Decimal('0.00'))
            elif f['MesFactura']:  
                horas += Decimal(str(f['MesFactura'])) * hh.get('horas_mes', Decimal('0.00'))
            
            total_valor += Decimal(str(f['Valor'] or '0'))
            total_horas += horas
    
    return {'valor': total_valor, 'horas': total_horas}  # Devuelve ambos valores

def obtener_ipc_anio(anio):
    """Obtiene el IPC de un año (retorna 1 si no existe)"""
    try:
        ipc = IPC.objects.filter(Anio=str(anio)).order_by('-Mes').first()
        return ipc.Indice if ipc else 1
    except Exception:
        return 1

@login_required
@verificar_permiso('can_view_indicadores_margen_cliente')
def indicadores_margen_cliente(request):
    form = Ind_Totales_FilterForm(request.GET or None)
    resultados = None
    anio = None
    clientes = Clientes.objects.all().order_by('Nombre_Cliente')
    lineas_seleccionadas = Linea.objects.all()

    if form.is_valid():
        anio = form.cleaned_data['Anio']
        meses = [str(m) for m in sorted(form.cleaned_data['Mes'])] if form.cleaned_data['Mes'] else [str(m) for m in range(1, 13)]
        lineas_seleccionadas = form.cleaned_data['LineaId'] or Linea.objects.all()
        clientes = form.cleaned_data['ClienteId'] or Clientes.objects.all().order_by('Nombre_Cliente')
        lineas_ids = [l.LineaId for l in lineas_seleccionadas] 
        horas_habiles = obtener_horas_habiles(anio)
        datos_precargados = precargar_datos(anio, meses, clientes, lineas_seleccionadas)
        tiempos_data = datos_precargados['tiempos_data']
        facturacion_data = datos_precargados['facturacion_data']
        
        # Calcular resultados para cada cliente
        client_totals = {}
        for cliente in clientes:
            costo_total = Decimal('0.00')
            facturado_valor_total = Decimal('0.00')
            trabajado_total = Decimal('0.00')  # Total horas trabajadas
            facturado_horas_total = Decimal('0.00')  # Total horas facturadas
            
            # Calcular por cada mes
            for mes in meses:
                if mes not in horas_habiles:
                    continue
                    
                hh_mes = horas_habiles[mes]
                
                # Calcular trabajado y costo
                trabajado = calcular_trabajado(cliente.ClienteId, anio, mes, lineas_ids, tiempos_data)
                costo = calcular_costo(
                    cliente.ClienteId, mes, lineas_ids, tiempos_data, 
                    hh_mes, datos_precargados['nominas_dict'], 
                    datos_precargados['tarifas_consultores_dict']
                )
                
                # Calcular facturado (ahora devuelve valor y horas)
                facturado = calcular_facturado(anio, mes, cliente, lineas_ids, facturacion_data, horas_habiles)
                
                costo_total += costo
                facturado_valor_total += facturado['valor']
                trabajado_total += trabajado
                facturado_horas_total += facturado['horas']
            
            # Calcular pendiente CORRECTO
            tarifas_cliente = datos_precargados['tarifas_por_cliente'].get(cliente.ClienteId, [])
            tarifa_valor = Decimal('0.00')
            if tarifas_cliente:
                # Tomar la última tarifa
                tarifa = sorted(tarifas_cliente, key=lambda x: (-int(x.anio), -int(x.mes)))[0]
                if tarifa.valorHora:
                    tarifa_valor = tarifa.valorHora
                elif tarifa.valorDia:
                    tarifa_valor = tarifa.valorDia / 8  # 8 horas por día
                elif tarifa.valorMes:
                    tarifa_valor = tarifa.valorMes / 160  # 160 horas por mes
            
            # Calcular horas pendientes de facturar
            horas_pendientes = max(Decimal('0.00'), trabajado_total - facturado_horas_total)
            pendiente_valor_total = horas_pendientes * tarifa_valor
            
            # Calcular totales
            total_facturado = facturado_valor_total + pendiente_valor_total
            utilidad_bruta = total_facturado - costo_total
            
            try:
                margen_bruto = (utilidad_bruta / total_facturado * 100) if total_facturado > 0 else 0
            except InvalidOperation:
                margen_bruto = 0
            
            client_totals[cliente.Nombre_Cliente] = {
                'Costo': costo_total,
                'Facturado_valor': facturado_valor_total,
                'Pendiente_valor': pendiente_valor_total,
                'total_facturado': total_facturado,
                'utilidad_bruta': utilidad_bruta,
                'margen_bruto': margen_bruto
            }
        
        # Calcular totales agregados
        costos_totales = sum(d['Costo'] for d in client_totals.values())
        facturados_totales = sum(d['Facturado_valor'] for d in client_totals.values())
        pendientes_totales = sum(d['Pendiente_valor'] for d in client_totals.values())
        totales_facturados = sum(d['total_facturado'] for d in client_totals.values())
        utilidades_totales = sum(d['utilidad_bruta'] for d in client_totals.values())
        
        try:
            margen_bruto_total = (utilidades_totales / totales_facturados * 100) if totales_facturados > 0 else 0
        except InvalidOperation:
            margen_bruto_total = 0
        
        resultados = {
            'totales': client_totals,
            'totales_agregados': {
                'costo_total': costos_totales,
                'facturado_valor_total': facturados_totales,
                'pendiente_valor_total': pendientes_totales,
                'total_facturado_total': totales_facturados,
                'utilidad_bruta_total': utilidades_totales,
                'margen_bruto_total': margen_bruto_total
            }
        }

    context = {
        'form': form,
        'resultados': resultados,
        'anio': anio,
        'Lineas': lineas_seleccionadas,
    }
    return render(request, 'Indicadores/IndicadoresMargenCliente.html', context)