from django.db.models import Sum, Q, F
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from django.shortcuts import render
from django.core.cache import cache
from Modulo.forms import Ind_Totales_FilterForm
from Modulo.models import Clientes, Concepto, FacturacionClientes, Horas_Habiles, Ind_Totales_Diciembre, Linea, Nomina, Tarifa_Clientes, Tarifa_Consultores, Tiempos_Cliente, TiemposConcepto

MESES = {
    '1': 'Enero', '2': 'Febrero', '3': 'Marzo', '4': 'Abril',
    '5': 'Mayo', '6': 'Junio', '7': 'Julio', '8': 'Agosto',
    '9': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
}

# Funciones auxiliares

# 1. Función para obtener días y horas hábiles
def obtener_horas_habiles(anio: str) -> dict:
    """Obtiene días y horas hábiles por mes para un año específico con cache"""
    cache_key = f'horas_habiles_{anio}'
    if cached := cache.get(cache_key):
        return cached
    
    registros = Horas_Habiles.objects.filter(Anio=anio)
    data = {
        str(r.Mes): {
            'dias': r.Dias_Habiles,
            'horas_mes': r.Dias_Habiles * r.Horas_Laborales,
            'horas_diarias': r.Horas_Laborales
        } for r in registros
    }
    cache.set(cache_key, data, 3600)
    return data

def precargar_datos(anio: str, meses: list, clientes: list, lineas: list, horas_habiles: dict):
    """Precarga todos los datos necesarios para optimizar consultas"""
    clientes_ids = [c.ClienteId for c in clientes]
    lineas_ids = [l.LineaId for l in lineas]
    meses_int = [int(m) for m in meses]

    # Determinar si se necesita diciembre del año anterior
    anio_anterior = str(int(anio) - 1)
    meses_tiempos = meses_int.copy()
    if 1 in meses_int:
        meses_tiempos.append(12)  # Añadir diciembre del año anterior
        anios_tiempos = [anio, anio_anterior]
    else:
        anios_tiempos = [anio]

    # Precargar tiempos incluyendo diciembre del año anterior si aplica 
    tiempos = Tiempos_Cliente.objects.filter(
        Anio__in=anios_tiempos,
        Mes__in=meses_tiempos,
        ClienteId__in=clientes_ids,
        LineaId__in=lineas_ids
    )
    tiempos_data = list(tiempos)
    
    # Precargar facturación con cálculo correcto de horas
    meses_facturacion = [int(m) for m in meses]
    facturacion = FacturacionClientes.objects.filter(
        Anio=int(anio),
        Mes__in=meses_facturacion,  
        ClienteId__in=clientes_ids,
        LineaId__in=lineas_ids
    )
    facturacion_data = defaultdict(lambda: {'horas': Decimal('0.00'), 'valor': Decimal('0.00')})
    for f in facturacion:
        mes = str(f.Mes)
        hh = horas_habiles.get(mes, {})
        horas = Decimal('0.00')
        
        if f.HorasFactura:
            horas += Decimal(str(f.HorasFactura))
        elif f.DiasFactura:
            horas += Decimal(str(f.DiasFactura)) * hh.get('horas_diarias', Decimal('0.00'))
        elif f.MesFactura:
            horas += Decimal(str(f.MesFactura)) * hh.get('horas_mes', Decimal('0.00'))
        
        key = (f.ClienteId.ClienteId, anio, mes, f.LineaId.LineaId)
        facturacion_data[key]['horas'] += horas
        facturacion_data[key]['valor'] += Decimal(str(f.Valor or '0'))
    
    # Precargar nóminas y tarifas consultores
    nominas = Nomina.objects.all().values('Documento', 'Anio', 'Mes', 'Salario')
    nominas_dict = defaultdict(list)
    for n in nominas:
        doc = n['Documento']
        anio_int = int(n['Anio'])
        mes_int = int(n['Mes'])
        nominas_dict[doc].append( (anio_int, mes_int, Decimal(str(n['Salario'] or '0')) ))
    # Ordenar por año y mes descendente
    for doc in nominas_dict:
        nominas_dict[doc].sort(key=lambda x: (-x[0], -x[1]))

    # Precargar todas las tarifas de consultores históricas
    tarifas_consultores = Tarifa_Consultores.objects.all().values(
        'documentoId', 'anio', 'mes', 'valorHora', 'valorDia', 'valorMes'
    )
    tarifas_consultores_dict = defaultdict(list)
    for t in tarifas_consultores:
        doc = t['documentoId']
        anio_int = int(t['anio'])
        mes_int = int(t['mes'])
        tarifas_consultores_dict[doc].append((
            anio_int, 
            mes_int,
            Decimal(str(t['valorHora'] or '0')),
            Decimal(str(t['valorDia'] or '0')),
            Decimal(str(t['valorMes'] or '0'))
        ))
    # Ordenar por año y mes descendente
    for doc in tarifas_consultores_dict:
        tarifas_consultores_dict[doc].sort(key=lambda x: (-x[0], -x[1]))
    
    # Precargar tarifas clientes
    tarifas_clientes = Tarifa_Clientes.objects.filter(clienteId__in=clientes_ids).select_related('clienteId')
    tarifas_por_cliente = defaultdict(list)
    for tarifa in tarifas_clientes:
        tarifas_por_cliente[tarifa.clienteId_id].append(tarifa)
    
    return {
        'tiempos_data': tiempos_data,
        'facturacion_data': facturacion_data,
        'nominas_dict': nominas_dict,
        'tarifas_consultores_dict': tarifas_consultores_dict,
        'tarifas_por_cliente': tarifas_por_cliente
    }

# 2. Función para calcular horas trabajadas por cliente
def calcular_trabajado(cliente_id: str, anio: str, mes: str, lineas_ids: list, tiempos_data: list) -> Decimal:
    """Calcula horas trabajadas usando datos precargados"""
    return sum(
        t.Horas for t in tiempos_data 
        if t.ClienteId_id == cliente_id and t.Anio == anio and t.Mes == mes and t.LineaId_id in lineas_ids
    )

# 3. Función para calcular costos
def calcular_costo(cliente_id: str, mes: str, lineas_ids: list, tiempos_data: list, hh_mes: dict, nominas_dict: dict, tarifas_consultores_dict: dict) -> Decimal:
    total = Decimal('0.00')
    mes_int = int(mes)
    
    for tiempo in tiempos_data:
        if tiempo.ClienteId_id != cliente_id or tiempo.Mes != mes or tiempo.LineaId_id not in lineas_ids:
            continue

        documento = tiempo.Documento
        anio_int = int(tiempo.Anio)
        costo_hora = Decimal('0.00')  # Inicializar con valor por defecto
        
        # Lógica para empleados
        if documento in nominas_dict:
            entradas_nomina = nominas_dict[documento]
            entrada = encontrar_entrada_anterior(entradas_nomina, anio_int, mes_int)
            if entrada:
                salario = entrada[2]
                horas_mes_total = hh_mes.get('horas_mes', Decimal('1'))
                costo_hora = salario / horas_mes_total if horas_mes_total else Decimal('0')
        
        # Lógica para consultores
        else:
            entradas_tarifa = tarifas_consultores_dict.get(documento, [])
            entrada = encontrar_entrada_anterior(entradas_tarifa, anio_int, mes_int)
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

        total += tiempo.Horas * costo_hora
    
    return total

def encontrar_entrada_anterior(entradas, anio_objetivo, mes_objetivo):
    for entrada in entradas:
        anio_entrada, mes_entrada = entrada[0], entrada[1]
        if anio_entrada < anio_objetivo:
            return entrada
        elif anio_entrada == anio_objetivo and mes_entrada <= mes_objetivo:
            return entrada
    return None

# 4. Función para facturación
def calcular_facturado(anio: str, mes: str, cliente: Clientes, lineas_ids: list, facturacion_data: dict) -> dict:
    """Calcula facturación usando datos precargados"""
    total_horas = Decimal('0.00')
    total_valor = Decimal('0.00')
    for linea_id in lineas_ids:
        key = (cliente.ClienteId, anio, mes, linea_id)
        if key in facturacion_data:
            total_horas += facturacion_data[key]['horas']
            total_valor += facturacion_data[key]['valor']
    return {'horas': total_horas, 'valor': total_valor}

# 5. Función para pendientes de facturación
def calcular_pendiente(anio: str, mes: str, cliente: Clientes, lineas_ids: list, trabajado_actual: Decimal, facturado_actual: Decimal, horas_habiles: dict, tarifas_por_cliente: dict, 
                      tiempos_data: list,
                      pendiente_anterior: Decimal = None) -> dict:    
    try:
        if pendiente_anterior is None:
            # Obtener datos de diciembre usando la nueva estructura
            datos_diciembre = calcular_pendiente_diciembre(anio, cliente)
            trabajado_anterior = datos_diciembre['trabajado']
            facturado_anterior = datos_diciembre['facturado']
            
            # Asegurar que todos los valores son Decimal
            trabajado_actual = Decimal(trabajado_actual)
            facturado_actual = Decimal(facturado_actual)
            
            pendiente_horas = (trabajado_anterior + trabajado_actual) - (facturado_anterior + facturado_actual)
        else:
            pendiente_horas = (pendiente_anterior + trabajado_actual) - facturado_actual
            trabajado_anterior = pendiente_anterior
        
        # Selección correcta de tarifa
        tarifas_cliente = tarifas_por_cliente.get(cliente.ClienteId, [])
        tarifa = None
        for t in sorted(tarifas_cliente, key=lambda x: (-int(x.anio), -int(x.mes))):
            if (int(t.anio) < int(anio)) or (int(t.anio) == int(anio) and int(t.mes) <= int(mes)):
                tarifa = t
                break
        
        tarifa_valor = Decimal('0.00')
        if tarifa:
            hh = horas_habiles.get(mes, {})
            if tarifa.valorHora:
                tarifa_valor = tarifa.valorHora
            elif tarifa.valorDia:
                tarifa_valor = tarifa.valorDia / hh.get('horas_diarias', Decimal('1.00'))
            elif tarifa.valorMes:
                tarifa_valor = tarifa.valorMes / hh.get('horas_mes', Decimal('1.00'))
        
        return {
            'trabajado_anterior': trabajado_anterior,
            'horas': pendiente_horas,
            'valor': pendiente_horas * tarifa_valor
        }
    except Exception as e:
        print(f"Error calculando pendiente: {str(e)}")
        return {'trabajado_anterior': Decimal('0.00'), 'horas': Decimal('0.00'), 'valor': Decimal('0.00')}

def calcular_pendiente_diciembre(anio: str, cliente: Clientes):
    """Obtiene los valores de diciembre del año anterior desde la nueva estructura"""
    try:
        registro = Ind_Totales_Diciembre.objects.get(
            Anio=int(anio)-1,
            Mes=12,
            ClienteId=cliente
        )
        return {
            'trabajado': Decimal(str(registro.Trabajado)),
            'facturado': Decimal(str(registro.Facturado)), 
            'costo': Decimal(str(registro.Costo)),
            'valor_facturado': Decimal(str(registro.ValorFacturado))
        }
    except Ind_Totales_Diciembre.DoesNotExist:
        return {
            'trabajado': Decimal('0'),
            'facturado': Decimal('0'),
            'costo': Decimal('0'),
            'valor_facturado': Decimal('0')
        }
    
def guardar_pendiente_diciembre(
    anio: str,
    cliente_id: int,
    trabajado: Decimal,
    facturado: Decimal,
    costo: Decimal,
    valor_facturado: Decimal
):
    """Guarda los valores en Decimal sin redondear"""
    try:
        trabajado = max(trabajado, Decimal('0'))
        facturado = max(facturado, Decimal('0'))
        costo = max(costo, Decimal('0'))
        valor_facturado = max(valor_facturado, Decimal('0'))

        Ind_Totales_Diciembre.objects.update_or_create(
            Anio=int(anio)-1,
            Mes=12,
            ClienteId_id=cliente_id,
            defaults={
                'Trabajado': trabajado,
                'Facturado': facturado,
                'Costo': costo,
                'ValorFacturado': valor_facturado
            }
        )
    except Exception as e:
        print(f"Error guardando diciembre: {e}")

def guardar_pendiente_anual(
    anio: int,
    cliente_id: int,
    pendiente_horas: Decimal,
    pendiente_valor: Decimal
):
    """Guarda pendientes anuales con Decimal"""
    try:
        trabajado = max(pendiente_horas, Decimal('0'))
        facturado = abs(min(pendiente_horas, Decimal('0')))
        costo = max(pendiente_valor, Decimal('0'))
        valor_facturado = abs(min(pendiente_valor, Decimal('0')))

        if trabajado == 0 and facturado == 0 and costo == 0 and valor_facturado == 0:
            return

        Ind_Totales_Diciembre.objects.update_or_create(
            Anio=anio,
            Mes=12,
            ClienteId_id=cliente_id,
            defaults={
                'Trabajado': trabajado,
                'Facturado': facturado,
                'Costo': costo,
                'ValorFacturado': valor_facturado
            }
        )
    except Exception as e:
        print(f"Error guardando anual: {e}")

# 6. Función para obtener conceptos
def obtener_conceptos(anio: str, mes: str) -> dict:
    """Obtiene horas por concepto para un mes específico"""
    conceptos = TiemposConcepto.objects.filter(
        Anio=anio, Mes=mes
    ).values('ConceptoId__Descripcion').annotate(total=Sum('Horas'))
    
    return {c['ConceptoId__Descripcion']: c['total'] for c in conceptos}

def calcular_totales_generales(resultados: dict, num_meses: int):
    resultados['totales']['Dias'] = sum(
        mes['Dias'] for mes in resultados['general'].values()
    ) / num_meses if num_meses > 0 else 0
    resultados['totales']['Horas'] = sum(
        mes['Horas'] for mes in resultados['general'].values()
    ) / num_meses if num_meses > 0 else 0
    
    conceptos_totales = defaultdict(Decimal)
    for mes_data in resultados['general'].values():
        for concepto, horas in mes_data['Conceptos_Horas'].items():
            conceptos_totales[concepto] += horas
    resultados['totales']['Conceptos_Horas'] = conceptos_totales

def calcular_diferencias_margen(resultados: dict):
    for cliente_nombre, datos in resultados['totales'].items():
        if cliente_nombre in ['Dias', 'Horas', 'Conceptos_Horas']:
            continue
        try:
            datos['Dif_Fact_Horas'] = datos['Trabajado'] - datos['Facturado_horas'] - datos['Pendiente_horas']
            datos['Dif_Fact_Valor'] = (datos['Facturado_valor'] + datos['Pendiente_valor']) - datos['Costo']
            datos['Margen_Bruto'] = ((datos['Facturado_valor'] + datos['Pendiente_valor'] - datos['Costo']) / (datos['Facturado_valor'] + datos['Pendiente_valor'])) * 100 if (datos['Facturado_valor'] + datos['Pendiente_valor']) != 0 else 0
        except KeyError as e:
            print(f"Error calculando margen para {cliente_nombre}: {str(e)}")
            datos['Margen_Bruto'] = 0

def calcular_margen_bruto(facturado_total: Decimal, pendiente_total: Decimal, costo_total: Decimal) -> Decimal:
    """Calcula el porcentaje de margen bruto"""
    total_facturado = facturado_total + pendiente_total
    if total_facturado == 0:
        return Decimal('0.00')
    return ((total_facturado - costo_total) / total_facturado * 100).quantize(Decimal('0.01'))

def calcular_trabajado_por_linea(mes: str, linea_id: int, tiempos_data: list) -> Decimal:
    """Calcula horas trabajadas para una línea usando datos precargados"""
    return sum(
        t.Horas for t in tiempos_data
        if str(t.Mes) == mes and t.LineaId_id == linea_id
    )

def calcular_costo_por_linea(anio: str, mes: str, linea: Linea, horas_habiles: dict, clientes: list, datos_precargados: dict) -> Decimal:
    """Calcula costo total para una línea y mes específico sumando todos los clientes"""
    total = Decimal('0.00')
    for cliente in clientes:
        total += calcular_costo(
            cliente.ClienteId,  # <-- Usar ID del cliente
            mes,
            [linea.LineaId],  # <-- Pasar lista de IDs de línea, no objetos
            datos_precargados['tiempos_data'],
            horas_habiles,
            datos_precargados['nominas_dict'], 
            datos_precargados['tarifas_consultores_dict']
        )
    return total

def calcular_facturado_por_linea(anio: str, mes: str, linea: Linea, horas_habiles: dict, clientes: list) -> dict:
    """Calcula facturación total para una línea y mes específico sumando todos los clientes"""
    total_horas = Decimal('0.00')
    total_valor = Decimal('0.00')
    for cliente in clientes:
        facturado = calcular_facturado(anio, mes, cliente, [linea.LineaId], horas_habiles)
        total_horas += facturado['horas']
        total_valor += facturado['valor']
    return {'horas': total_horas, 'valor': total_valor}

def calcular_pendiente_por_linea(anio: str, mes: str, linea: Linea, horas_habiles: dict, clientes: list, datos_precargados: dict) -> dict:
    """Calcula pendientes de facturación para una línea y mes específico sumando todos los clientes"""
    total_horas = Decimal('0.00')
    total_valor = Decimal('0.00')
    for cliente in clientes:

        trabajado_cliente = calcular_trabajado(
            cliente.ClienteId, 
            anio,
            mes,
            [linea.LineaId], 
            datos_precargados['tiempos_data']
        )
        facturado_cliente = calcular_facturado(anio, mes, cliente, [linea.LineaId], datos_precargados['facturacion_data'])['horas']
        pendiente_cliente = calcular_pendiente(
            anio, mes, cliente, [linea.LineaId], 
            trabajado_cliente, facturado_cliente, 
            horas_habiles, datos_precargados['tarifas_por_cliente'],
            datos_precargados['tiempos_data']
        )
        total_horas += pendiente_cliente['horas']
        total_valor += pendiente_cliente['valor']
    return {'horas': total_horas, 'valor': total_valor}

def indicadores_totales(request):
    form = Ind_Totales_FilterForm(request.GET or None)
    resultados = {
        'general': defaultdict(dict),
        'totales': defaultdict(lambda: defaultdict(Decimal)),
        'lineas': {},
        'conceptos': Concepto.objects.all()
    }
    valores_diciembre = {}  # Para almacenar los valores de diciembre del año anterior
    anio = None  # Inicializar la variable anio
    
    if form.is_valid():
        anio = form.cleaned_data['Anio']
        meses = [str(m) for m in sorted(form.cleaned_data['Mes'])] if form.cleaned_data['Mes'] else [str(m) for m in range(1, 13)]
        lineas_seleccionadas = form.cleaned_data['LineaId'] or Linea.objects.all()
        clientes = form.cleaned_data['ClienteId'] or Clientes.objects.all()
        lineas_ids = [l.LineaId for l in lineas_seleccionadas]
        clientes_ids = [c.ClienteId for c in clientes]
        
        horas_habiles = obtener_horas_habiles(anio)
        datos_precargados = precargar_datos(anio, meses, clientes, lineas_seleccionadas, horas_habiles)
        tiempos_data = datos_precargados['tiempos_data']

        # Calcular valores de diciembre del año anterior
        anio_anterior = str(int(anio) - 1)
        for cliente in clientes:
            valores_diciembre[cliente.ClienteId] = calcular_pendiente_diciembre(anio, cliente)
        
        # Procesamiento general
        for mes in meses:
            if mes not in horas_habiles:
                continue
                
            hh = horas_habiles[mes]
            resultados['general'][mes] = {
                'Dias': hh['dias'],
                'Horas': hh['horas_mes'],
                'Clientes': {},
                'Conceptos_Horas': obtener_conceptos(anio, mes),
                'totales_mes': {
                    'costo_no_op': Decimal('0.00'),
                    'costo_vacaciones': Decimal('0.00'),
                    'costo_incapacidades': Decimal('0.00'),
                    'total_horas': sum(obtener_conceptos(anio, mes).values())
                }
            }
            
            for cliente in clientes:
                trabajado = calcular_trabajado(cliente.ClienteId,anio, mes, lineas_ids, tiempos_data)
                costo = calcular_costo(cliente.ClienteId, mes, lineas_ids, tiempos_data, hh, datos_precargados['nominas_dict'], datos_precargados['tarifas_consultores_dict'])
                fact_key = (cliente.ClienteId, anio, mes, lineas_ids[0])  # Ajustar según estructura real
                facturado = datos_precargados['facturacion_data'].get(fact_key, {'horas': Decimal('0.00'), 'valor': Decimal('0.00')})
                
                if mes == '1':
                    pendiente = calcular_pendiente(
                        anio, mes, cliente, lineas_ids, 
                        trabajado, facturado['horas'], 
                        horas_habiles, 
                        datos_precargados['tarifas_por_cliente'],
                        tiempos_data 
                    )
                else:
                    mes_anterior = str(int(mes) - 1)
                    pendiente_anterior = (
                        resultados['general'][mes_anterior]['Clientes'][cliente.Nombre_Cliente]['Pendiente']['horas']
                        if mes_anterior in resultados['general'] and cliente.Nombre_Cliente in resultados['general'][mes_anterior]['Clientes']
                        else Decimal('0.00')
                    )
                    pendiente = calcular_pendiente(
                        anio, mes, cliente, lineas_ids, 
                        trabajado, facturado['horas'], 
                        horas_habiles, 
                        datos_precargados['tarifas_por_cliente'],
                        tiempos_data, 
                        pendiente_anterior
                    )
                
                # Actualizar resultados
                resultados['general'][mes]['Clientes'][cliente.Nombre_Cliente] = {
                    'Trabajado': trabajado,
                    'Costo': costo,
                    'Facturado': facturado,
                    'Pendiente': pendiente,
                    'Trabajado_Anterior': pendiente['trabajado_anterior']
                }

                # Acumular totales
                for campo in ['Trabajado', 'Costo']:
                    resultados['totales'][cliente.Nombre_Cliente][campo] += resultados['general'][mes]['Clientes'][cliente.Nombre_Cliente][campo]
                for tipo in ['horas', 'valor']:
                    resultados['totales'][cliente.Nombre_Cliente][f'Facturado_{tipo}'] += facturado[tipo]
                    resultados['totales'][cliente.Nombre_Cliente][f'Pendiente_{tipo}'] = pendiente[tipo]
        
        # Procesamiento por línea
        for linea in lineas_seleccionadas:
            line_data = {
                'nombre': linea.Linea,
                'general': {},
                'totales': {
                    'Trabajado': Decimal('0.00'),
                    'Costo': Decimal('0.00'),
                    'Facturado_horas': Decimal('0.00'),
                    'Facturado_valor': Decimal('0.00'),
                    'Pendiente_horas': Decimal('0.00'),
                    'Pendiente_valor': Decimal('0.00'),
                    'TotalFacturado_horas': Decimal('0.00'),
                    'TotalFacturado_valor': Decimal('0.00'),
                    'Dif_Horas': Decimal('0.00'),
                    'Dif_Valor': Decimal('0.00'),
                    'Margen': Decimal('0.00'),
                }
            }

            for mes in meses:
                if mes not in horas_habiles:
                    continue

                hh = horas_habiles[mes]

                trabajado = calcular_trabajado_por_linea(mes, linea.LineaId, datos_precargados['tiempos_data'])
                costo = calcular_costo_por_linea(anio, mes, linea, horas_habiles, clientes, datos_precargados)
                facturado = calcular_facturado_por_linea(anio, mes, linea, horas_habiles, clientes)
                pendiente = calcular_pendiente_por_linea(anio, mes, linea, horas_habiles, clientes, datos_precargados)

                total_facturado_horas = facturado['horas'] + pendiente['horas']
                total_facturado_valor = facturado['valor'] + pendiente['valor']
                dif_horas = trabajado - total_facturado_horas
                dif_valor = (facturado['valor'] + pendiente['valor']) - costo
                margen = calcular_margen_bruto(facturado['valor'], pendiente['valor'], costo)

                line_mes_data = {
                    'Dias': hh['dias'],
                    'Horas': hh['horas_mes'],
                    'Trabajado': trabajado,
                    'Costo': costo,
                    'Facturado': facturado,
                    'Pendiente': pendiente,
                    'TotalFacturado': {
                        'horas': total_facturado_horas,
                        'valor': total_facturado_valor
                    },
                    'Dif_Horas': dif_horas,
                    'Dif_Valor': dif_valor,
                    'Margen': margen
                }

                # Acumular totales de la línea
                line_data['totales']['Trabajado'] += trabajado
                line_data['totales']['Costo'] += costo
                line_data['totales']['Facturado_horas'] += facturado['horas']
                line_data['totales']['Facturado_valor'] += facturado['valor']
                line_data['totales']['Pendiente_horas'] = pendiente['horas']
                line_data['totales']['Pendiente_valor'] = pendiente['valor']
                line_data['totales']['TotalFacturado_horas'] += total_facturado_horas
                line_data['totales']['TotalFacturado_valor'] += total_facturado_valor
                line_data['totales']['Dif_Horas'] += dif_horas
                line_data['totales']['Dif_Valor'] += dif_valor

                line_data['general'][mes] = line_mes_data

            # Calcular margen total para la línea
            total_facturado_valor = line_data['totales']['Facturado_valor'] + line_data['totales']['Pendiente_valor']
            total_costo = line_data['totales']['Costo']
            margen_total = calcular_margen_bruto(total_facturado_valor, line_data['totales']['Pendiente_valor'], total_costo)
            line_data['totales']['Margen'] = margen_total

            resultados['lineas'][linea.LineaId] = line_data

        # Cálculos finales generales
        num_meses = len(resultados['general']) or 1
        calcular_totales_generales(resultados, num_meses)
        calcular_diferencias_margen(resultados)

    if request.method == 'POST':
        anio_actual = int(anio)
        
        # Guardar datos de diciembre del año anterior (inputs manuales)
        for cliente in clientes:
            cliente_id = cliente.ClienteId
            
            trabajado = Decimal(request.POST.get(f'diciembre_trabajado_{cliente_id}', 0) or Decimal(0))
            facturado = Decimal(request.POST.get(f'diciembre_facturado_{cliente_id}', 0) or Decimal(0))
            costo = Decimal(request.POST.get(f'diciembre_costo_{cliente_id}', 0) or Decimal(0))
            valor_facturado = Decimal(request.POST.get(f'diciembre_valor_facturado_{cliente_id}', 0) or Decimal(0))

            # Guardar para diciembre del año anterior
            guardar_pendiente_diciembre(
                anio=str(anio_actual),
                cliente_id=cliente_id,
                trabajado=trabajado,  # Mantener como Decimal
                facturado=facturado,
                costo=costo,
                valor_facturado=valor_facturado
            )
        
        # Guardar pendientes finales del año actual
        for cliente in clientes:
            if meses:
                ultimo_mes = meses[-1]
                # Verificar que el último mes existe en los resultados
                if ultimo_mes in resultados['general']:
                    ultimo_pendiente = resultados['general'][ultimo_mes]['Clientes'][cliente.Nombre_Cliente]['Pendiente']
                else:
                    ultimo_pendiente = {'horas': Decimal('0'), 'valor': Decimal('0')}
            
            guardar_pendiente_anual(
                anio=anio_actual,
                cliente_id=cliente.ClienteId,
                pendiente_horas=ultimo_pendiente['horas'],
                pendiente_valor=ultimo_pendiente['valor']
            )
            
    resultados['general'] = dict(resultados['general'])
    context = {
        'form': form,
        'resultados': resultados,
        'valores_diciembre': valores_diciembre,  # Pasar los valores de diciembre al contexto
        'anio': anio,
        'MESES': MESES,
        'Clientes': clientes if form.is_valid() else [],
        'Lineas': lineas_seleccionadas if form.is_valid() else [],
        'Conceptos': resultados['conceptos']
    }
    return render(request, 'Indicadores/indicadores_totales.html', context)