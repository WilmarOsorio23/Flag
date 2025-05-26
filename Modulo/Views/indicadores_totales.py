from django.db.models import Sum, Q, F
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from django.db import transaction
from django.shortcuts import redirect, render
from django.core.cache import cache
from django.http import JsonResponse
import json
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
    ).select_related('ClienteId', 'LineaId').values(
        'Anio', 'Mes', 'Documento', 'ClienteId', 'LineaId', 'Horas', 'ModuloId'
    )
    tiempos_data = list(tiempos)
    
    # Precargar facturación con cálculo correcto de horas
    meses_facturacion = [int(m) for m in meses]
    facturacion = FacturacionClientes.objects.filter(
        Anio=int(anio),
        Mes__in=meses_facturacion
    ).values('ClienteId', 'LineaId', 'Mes', 'HorasFactura', 'DiasFactura', 'MesFactura', 'Valor')
    
    facturacion_data = defaultdict(lambda: {'horas': Decimal('0.00'), 'valor': Decimal('0.00')})
    for f in facturacion:
        mes = str(f['Mes'])  # Corregido
        hh = horas_habiles.get(mes, {})
        horas = Decimal('0.00')
        
        if f['HorasFactura']: 
            horas += Decimal(str(f['HorasFactura']))
        elif f['DiasFactura']: 
            horas += Decimal(str(f['DiasFactura'])) * hh.get('horas_diarias', Decimal('0.00'))
        elif f['MesFactura']:  
            horas += Decimal(str(f['MesFactura'])) * hh.get('horas_mes', Decimal('0.00'))
        
        key = (f['ClienteId'], anio, mes, f['LineaId'])  
        facturacion_data[key]['horas'] += horas
        facturacion_data[key]['valor'] += Decimal(str(f['Valor'] or '0')) 
    
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
    'documentoId', 'anio', 'mes', 'valorHora', 'valorDia', 'valorMes', 'moduloId'
    )
    tarifas_consultores_dict = defaultdict(lambda: defaultdict(list))
    for t in tarifas_consultores:
        doc = t['documentoId']
        modulo_id = t['moduloId']  # Asumiendo que el modelo tiene este campo
        anio_int = int(t['anio'])
        mes_int = int(t['mes'])
        tarifas_consultores_dict[doc][modulo_id].append((
            anio_int, 
            mes_int,
            Decimal(str(t['valorHora'] or '0')),
            Decimal(str(t['valorDia'] or '0')),
            Decimal(str(t['valorMes'] or '0'))
        ))

    # Ordenar cada lista por año y mes descendente
    for doc in tarifas_consultores_dict:
        for modulo in tarifas_consultores_dict[doc]:
            tarifas_consultores_dict[doc][modulo].sort(key=lambda x: (-x[0], -x[1]))
    
    # Precargar tarifas clientes
    tarifas_clientes = Tarifa_Clientes.objects.filter(clienteId__in=clientes_ids
    ).select_related('clienteId').only(
        'clienteId', 'anio', 'mes', 'valorHora', 'valorDia', 'valorMes'
    )
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
        t['Horas'] for t in tiempos_data 
        if t['ClienteId'] == cliente_id
        and t['Anio'] == anio 
        and t['Mes'] == mes 
        and t['LineaId'] in lineas_ids
    )

# 3. Función para calcular costos
def calcular_costo(cliente_id: str, mes: str, lineas_ids: list, tiempos_data: list, hh_mes: dict, nominas_dict: dict, tarifas_consultores_dict: dict) -> Decimal:
    total = Decimal('0.00')
    mes_int = int(mes)
    
    for tiempo in tiempos_data:
        if tiempo['ClienteId'] != cliente_id or tiempo['Mes'] != mes or tiempo['LineaId'] not in lineas_ids:
            continue

        documento = tiempo['Documento']
        anio_int = int(tiempo['Anio'])
        modulo_id = tiempo['ModuloId']
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
            entradas_tarifa = tarifas_consultores_dict[documento].get(modulo_id, [])
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

        total += tiempo['Horas'] * costo_hora
    
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
                    pendiente_anterior: Decimal = None,
                    diciembre_data: dict = None) -> dict:    
    try:
        if pendiente_anterior is None:

            if diciembre_data is not None:
                trabajado_anterior = diciembre_data.get('trabajado', Decimal('0'))
                facturado_anterior = diciembre_data.get('facturado', Decimal('0'))
            else:
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

def guardar_pendientes_masivo(registros, es_anual=False):
    with transaction.atomic():
        a_crear = []
        a_actualizar = []
        
        # Obtener anio y mes basado en es_anual
        anio = registros[0]['anio'] if es_anual else registros[0]['anio'] - 1
        mes = 12
        
        # Obtener lista de IDs de clientes
        cliente_ids = [r['cliente_id'] for r in registros]
        
        # Obtener registros existentes
        existentes_queryset = Ind_Totales_Diciembre.objects.filter(
            ClienteId_id__in=cliente_ids,
            Anio=anio,
            Mes=mes
        )
        
        # Crear diccionario manual para manejar posibles duplicados
        existentes = {}
        for obj in existentes_queryset:
            cliente_id = obj.ClienteId_id
            if cliente_id not in existentes:
                existentes[cliente_id] = obj
            else:
                print(f"Advertencia: Duplicado encontrado para ClienteId {cliente_id} en {anio}-{mes}")
                pass
        
        # Procesar registros
        for registro in registros:
            cliente_id = registro['cliente_id']
            defaults = {
                'Trabajado': registro['trabajado'],
                'Facturado': registro['facturado'],
                'Costo': registro['costo'],
                'ValorFacturado': registro['valor_facturado']
            }
            
            if cliente_id in existentes:
                # Actualizar registro existente
                obj = existentes[cliente_id]
                for key, value in defaults.items():
                    setattr(obj, key, value)
                a_actualizar.append(obj)
            else:
                # Crear nuevo registro
                a_crear.append(Ind_Totales_Diciembre(
                    Anio=anio,
                    Mes=mes,
                    ClienteId_id=cliente_id,
                    **defaults
                ))
        
        # Ejecutar operaciones bulk
        Ind_Totales_Diciembre.objects.bulk_update(a_actualizar, ['Trabajado', 'Facturado', 'Costo', 'ValorFacturado'])
        Ind_Totales_Diciembre.objects.bulk_create(a_crear)
        
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
            # Usar la función calcular_margen_bruto para consistencia
            datos['Margen_Bruto'] = calcular_margen_bruto(
                datos['Facturado_valor'],
                datos['Pendiente_valor'],
                datos['Costo']
            )
        except KeyError as e:
            print(f"Error calculando margen para {cliente_nombre}: {str(e)}")
            datos['Margen_Bruto'] = Decimal('0.00')

def calcular_margen_bruto(facturado_total: Decimal, pendiente_total: Decimal, costo_total: Decimal) -> Decimal:
    """Calcula el porcentaje de margen bruto"""
    total_facturado = facturado_total + pendiente_total
    if total_facturado == 0:
        return Decimal('0.00')
    return ((total_facturado - costo_total) / total_facturado * 100).quantize(Decimal('0.01'))

def calcular_trabajado_por_linea(mes: str, linea_id: int, tiempos_data: list) -> Decimal:
    """Calcula horas trabajadas para una línea usando datos precargados"""
    return sum(
        t['Horas'] for t in tiempos_data
        if str(t['Mes']) == mes and t['LineaId'] == linea_id
    )

def calcular_costo_por_linea(anio: str, mes: str, linea: Linea, horas_habiles: dict, clientes: list, datos_precargados: dict) -> Decimal:
    """Calcula costo total para una línea y mes específico sumando todos los clientes"""
    total = Decimal('0.00')
    hh_mes = horas_habiles.get(mes, {})  # Obtener datos del mes específico
    for cliente in clientes:
        total += calcular_costo(
            cliente.ClienteId,
            mes,
            [linea.LineaId],
            datos_precargados['tiempos_data'],
            hh_mes,  # Pasar solo los datos del mes
            datos_precargados['nominas_dict'],
            datos_precargados['tarifas_consultores_dict']
        )
    return total

def calcular_facturado_por_linea(anio: str, mes: str, linea: Linea, clientes: list, facturacion_data: dict) -> dict:
    """Calcula facturación total para una línea y mes específico sumando todos los clientes"""
    total_horas = Decimal('0.00')
    total_valor = Decimal('0.00')
    for cliente in clientes:
        # Calcular facturación usando facturacion_data
        facturado = calcular_facturado(anio, mes, cliente, [linea.LineaId], facturacion_data)
        total_horas += facturado['horas']
        total_valor += facturado['valor']
    return {'horas': total_horas, 'valor': total_valor}

def calcular_pendiente_por_linea(anio: str, mes: str, linea: Linea, horas_habiles: dict, clientes: list, datos_precargados: dict, valores_diciembre: dict) -> dict:
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
        facturado_cliente = calcular_facturado(
            anio, mes, cliente, [linea.LineaId], 
            datos_precargados['facturacion_data']
        )['horas']
        
        # Obtener datos de diciembre si es enero
        dic_data = valores_diciembre.get(cliente.ClienteId, {}) if mes == '1' else None
        
        pendiente_cliente = calcular_pendiente(
            anio, mes, cliente, [linea.LineaId], 
            trabajado_cliente, facturado_cliente, 
            horas_habiles,
            datos_precargados['tarifas_por_cliente'],
            datos_precargados['tiempos_data'],
            diciembre_data=dic_data
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
    valores_diciembre = {}
    anio = None
    # Inicializar variables con valores por defecto
    clientes = Clientes.objects.all().order_by('Nombre_Cliente')
    lineas_seleccionadas = Linea.objects.all()
    
    # Manejo de solicitud AJAX para recálculo
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            
            # Validar que tengamos los datos necesarios
            if 'filters' not in data or 'diciembre' not in data or 'action' not in data:
                return JsonResponse({'error': 'Datos incompletos en la solicitud'}, status=400)
            
            # Procesar filtros
            filters = data['filters']
            form_ajax = Ind_Totales_FilterForm(filters)
            
            if not form_ajax.is_valid():
                return JsonResponse({
                    'error': 'Parámetros inválidos',
                    'details': form_ajax.errors
                }, status=400)

            anio = form_ajax.cleaned_data['Anio']
            meses = [str(m) for m in sorted(form_ajax.cleaned_data['Mes'])] if form_ajax.cleaned_data['Mes'] else [str(m) for m in range(1, 13)]
            lineas_seleccionadas = form_ajax.cleaned_data['LineaId'] or Linea.objects.all()
            clientes = form_ajax.cleaned_data['ClienteId'] or Clientes.objects.all().order_by('Nombre_Cliente')
            
            horas_habiles = obtener_horas_habiles(anio)
            datos_precargados = precargar_datos(anio, meses, clientes, lineas_seleccionadas, horas_habiles)

            # Procesar datos de diciembre
            valores_diciembre = {}
            for cliente_id, valores in data['diciembre'].items():
                try:
                    valores_diciembre[int(cliente_id)] = {
                        'trabajado': Decimal(str(valores.get('trabajado', 0))),
                        'facturado': Decimal(str(valores.get('facturado', 0))),
                        'costo': Decimal(str(valores.get('costo', 0))),
                        'valor_facturado': Decimal(str(valores.get('valor_facturado', 0)))
                    }
                except (ValueError, InvalidOperation) as e:
                    print(f"Error procesando valores para cliente {cliente_id}: {e}")
                    continue

            # Recalcular
            resultados = calcular_resultados(
                anio, meses, lineas_seleccionadas, clientes, 
                [l.LineaId for l in lineas_seleccionadas],
                [c.ClienteId for c in clientes],
                horas_habiles, 
                datos_precargados, 
                valores_diciembre
            )
            
            return JsonResponse({
                'general': resultados['general'],
                'totales': resultados['totales'],
                'lineas': resultados['lineas']
            })
            
        except Exception as e:
            print('Error en recálculo AJAX:', str(e))
            return JsonResponse({
                'error': 'Error interno del servidor',
                'details': str(e)
            }, status=500)

    if form.is_valid():
        anio = form.cleaned_data['Anio']
        meses = [str(m) for m in sorted(form.cleaned_data['Mes'])] if form.cleaned_data['Mes'] else [str(m) for m in range(1, 13)]
        lineas_seleccionadas = form.cleaned_data['LineaId'] or Linea.objects.all()
        clientes = form.cleaned_data['ClienteId'] or Clientes.objects.all().order_by('Nombre_Cliente')
        lineas_ids = [l.LineaId for l in lineas_seleccionadas]
        clientes_ids = [c.ClienteId for c in clientes]
        
        horas_habiles = obtener_horas_habiles(anio)
        datos_precargados = precargar_datos(anio, meses, clientes, lineas_seleccionadas, horas_habiles)
        tiempos_data = datos_precargados['tiempos_data']

        # Cargar valores iniciales de diciembre
        for cliente in clientes:
            valores_diciembre[cliente.ClienteId] = calcular_pendiente_diciembre(anio, cliente)
        
        resultados = calcular_resultados(
            anio, meses, lineas_seleccionadas, clientes, 
            lineas_ids, clientes_ids, horas_habiles, 
            datos_precargados, valores_diciembre
        )

    # Manejo de POST normal (guardado)
    if request.method == 'POST' and not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = Ind_Totales_FilterForm(request.POST)
        anio_actual = int(anio)
        
        # Guardar datos de diciembre del año anterior (inputs manuales)
        registros_diciembre = []
        registros_anuales = []
        for cliente in clientes:
            cliente_id = cliente.ClienteId
            datos = {
                'cliente_id': cliente_id,
                'anio': anio_actual,
                'trabajado': Decimal(request.POST.get(f'diciembre_trabajado_{cliente_id}', 0) or Decimal(0)),
                'facturado' : Decimal(request.POST.get(f'diciembre_facturado_{cliente_id}', 0) or Decimal(0)),
                'costo' : Decimal(request.POST.get(f'diciembre_costo_{cliente_id}', 0) or Decimal(0) ),
                'valor_facturado' : Decimal(request.POST.get(f'diciembre_valor_facturado_{cliente_id}', 0) or Decimal(0) )
            }
            registros_diciembre.append(datos)
            
            # Guardar pendientes finales del año actual
            if meses:
                ultimo_mes = meses[-1]
                if ultimo_mes in resultados['general']:
                    ultimo_pendiente = resultados['general'][ultimo_mes]['Clientes'][cliente.Nombre_Cliente]['Pendiente']
                else:
                    ultimo_pendiente = {'horas': Decimal('0'), 'valor': Decimal('0')}
                
                try:
                    trabajado = max(ultimo_pendiente['horas'], Decimal('0'))
                    facturado = abs(min(ultimo_pendiente['horas'], Decimal('0')))
                    costo = max(ultimo_pendiente['valor'], Decimal('0'))
                    valor_facturado = abs(min(ultimo_pendiente['valor'], Decimal('0')))

                    if trabajado == 0 and facturado == 0 and costo == 0 and valor_facturado == 0:
                        return
            
                    registros_anuales.append({
                        'cliente_id': cliente_id,
                        'anio': anio_actual,
                        'trabajado': trabajado,
                        'facturado': facturado,
                        'costo': costo,
                        'valor_facturado': valor_facturado
                    })
                except Exception as e:
                    print(f"Error guardando anual: {e}")
            # Guardado masivo
            guardar_pendientes_masivo(registros_diciembre)
            guardar_pendientes_masivo(registros_anuales, es_anual=True)
        
        # Recargar valores de diciembre DESPUÉS de guardar
        for cliente in clientes:
            valores_diciembre[cliente.ClienteId] = calcular_pendiente_diciembre(anio, cliente)
        
        # Recalcular resultados con nuevos valores
        if form.is_valid():
            resultados = calcular_resultados(
                anio, meses, lineas_seleccionadas, clientes, 
                lineas_ids, clientes_ids, horas_habiles, 
                datos_precargados, valores_diciembre
            )
        
        # Redireccionar para evitar reenvío de formulario
        return redirect(request.get_full_path())

    # Preparar contexto
    resultados['general'] = dict(resultados['general'])
    context = {
        'form': form,
        'resultados': resultados,
        'valores_diciembre': valores_diciembre,
        'anio': anio,
        'MESES': MESES,
        'Clientes': clientes,
        'Lineas': lineas_seleccionadas,
        'Conceptos': resultados['conceptos'],
        'Clientes_json': json.dumps([
            {'ClienteId': c.ClienteId, 'Nombre_Cliente': c.Nombre_Cliente} 
            for c in clientes.order_by('Nombre_Cliente')
        ])
    }
    return render(request, 'Indicadores/indicadores_totales.html', context)

def calcular_resultados(anio, meses, lineas_seleccionadas, clientes, lineas_ids, clientes_ids, horas_habiles, datos_precargados, valores_diciembre):
    """Función encapsulada para recalcular resultados con los mismos parámetros"""
    resultados = {
        'general': defaultdict(dict),
        'totales': defaultdict(lambda: defaultdict(Decimal)),
        'lineas': {},
        'conceptos': Concepto.objects.all()
    }
    
    tiempos_data = datos_precargados['tiempos_data']
    
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
            trabajado = calcular_trabajado(cliente.ClienteId, anio, mes, lineas_ids, tiempos_data)
            costo = calcular_costo(cliente.ClienteId, mes, lineas_ids, tiempos_data, hh, datos_precargados['nominas_dict'], datos_precargados['tarifas_consultores_dict'])
            fact_key = (cliente.ClienteId, anio, mes, lineas_ids[0])
            facturado = datos_precargados['facturacion_data'].get(fact_key, {'horas': Decimal('0.00'), 'valor': Decimal('0.00')})
            
            if mes == '1':
                # Obtener datos de diciembre del contexto (valores del usuario)
                dic_data = valores_diciembre.get(cliente.ClienteId, {
                    'trabajado': Decimal('0'),
                    'facturado': Decimal('0'),
                    'costo': Decimal('0'),
                    'valor_facturado': Decimal('0')
                })
                
                # Llamar a calcular_pendiente con diciembre_data
                pendiente = calcular_pendiente(
                    anio, mes, cliente, lineas_ids, 
                    trabajado, facturado['horas'], 
                    horas_habiles, 
                    datos_precargados['tarifas_por_cliente'],
                    tiempos_data,
                    None,  # Sin pendiente anterior
                    diciembre_data=dic_data  # Pasar los datos de diciembre
                )
            else:
                # Código existente para otros meses
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
    
    # Procesamiento por línea (igual que antes)
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
            facturado = calcular_facturado_por_linea(anio, mes, linea, clientes, datos_precargados['facturacion_data'])
            pendiente = calcular_pendiente_por_linea(anio, mes, linea, horas_habiles, clientes, datos_precargados, valores_diciembre)

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

            line_data['general'][mes] = line_mes_data
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

        total_facturado_valor = line_data['totales']['Facturado_valor'] + line_data['totales']['Pendiente_valor']
        total_costo = line_data['totales']['Costo']
        margen_total = calcular_margen_bruto(total_facturado_valor, line_data['totales']['Pendiente_valor'], total_costo)
        line_data['totales']['Margen'] = margen_total

        resultados['lineas'][linea.LineaId] = line_data

    # Cálculos finales generales
    num_meses = len(resultados['general']) or 1
    calcular_totales_generales(resultados, num_meses)
    calcular_diferencias_margen(resultados)

    return resultados