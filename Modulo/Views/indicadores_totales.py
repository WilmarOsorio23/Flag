from django.db.models import Sum
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from django.shortcuts import render
from Modulo.forms import Ind_Totales_FilterForm
from Modulo.models import Clientes, Concepto, FacturacionClientes, Horas_Habiles, Linea, Nomina, Tarifa_Clientes, Tarifa_Consultores, Tiempos_Cliente, TiemposConcepto

MESES = {
    '1': 'Enero', '2': 'Febrero', '3': 'Marzo', '4': 'Abril',
    '5': 'Mayo', '6': 'Junio', '7': 'Julio', '8': 'Agosto',
    '9': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
}

# Funciones auxiliares

# 1. Función para obtener días y horas hábiles
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


# 2. Función para calcular horas trabajadas por cliente
def calcular_trabajado(anio: str, mes: str, cliente: Clientes, lineas: list) -> Decimal:
    """Calcula horas trabajadas para un cliente y mes específico"""
    return Tiempos_Cliente.objects.filter(
        Anio=anio, Mes=mes, ClienteId=cliente.ClienteId,  LineaId__in=[linea.LineaId for linea in lineas]
    ).aggregate(total=Sum('Horas'))['total'] or Decimal('0.00')

# 3. Función para calcular costos
def calcular_costo(anio: str, mes: str, cliente: Clientes, lineas: list, horas_habiles: dict) -> Decimal:
    # Normalizar mes a 2 dígitos
    mes_normalizado = mes.zfill(2)

    tiempos = Tiempos_Cliente.objects.filter(
        Anio=anio, Mes=mes, ClienteId=cliente, LineaId__in=lineas
    )
    total = Decimal('0.00')
    hh_mes = horas_habiles.get(mes, {})
    
    for tiempo in tiempos:
        # Buscar en nómina
        nomina = Nomina.objects.filter(
            Anio=anio, Mes=mes_normalizado, Documento=tiempo.Documento
        ).first()
        
        if nomina and nomina.Salario:
            try:
                horas_totales = hh_mes.get('horas_mes', Decimal('1.00'))
                costo_hora = Decimal(nomina.Salario) / horas_totales
            except (InvalidOperation, ZeroDivisionError):
                costo_hora = Decimal('0.00')
        else:
            # Buscar en tarifas de consultores
            tarifa = Tarifa_Consultores.objects.filter(
                anio=anio, mes=mes_normalizado, clienteID=cliente, documentoId=tiempo.Documento
            ).first()
            costo_hora = obtener_valor_hora(tarifa, hh_mes) if tarifa else Decimal('0.00')
        
        total += tiempo.Horas * costo_hora
    return total

def obtener_valor_hora(tarifa, hh_mes):
    if not tarifa:
        return Decimal('0.00')
    if tarifa.valorHora and tarifa.valorHora > 0:
        return tarifa.valorHora
    elif tarifa.valorDia and tarifa.valorDia > 0:
        return tarifa.valorDia / hh_mes.get('horas_diarias', Decimal('1.00'))
    elif tarifa.valorMes and tarifa.valorMes > 0:
        return tarifa.valorMes / hh_mes.get('horas_mes', Decimal('1.00'))
    return Decimal('0.00')  

# 4. Función para facturación
def calcular_facturado(anio: str, mes: str, cliente: Clientes, lineas: list, horas_habiles: dict) -> dict:
    """Calcula valores facturados con diferentes modalidades (horas, días, meses)"""
    try:
        facturacion = FacturacionClientes.objects.filter(
            Anio=int(anio), Mes=int(mes), ClienteId=cliente, LineaId__in=lineas
        )
    except ValueError:
        return {'horas': Decimal('0.00'), 'valor': Decimal('0.00')}
    
    horas = Decimal('0.00')
    valor = Decimal('0.00')
    hh = horas_habiles.get(mes, {})
    
    for fact in facturacion:
        if fact.HorasFactura:
            horas += Decimal(str(fact.HorasFactura))
        elif fact.DiasFactura:
            horas += Decimal(str(fact.DiasFactura)) * hh.get('horas_diarias', Decimal('0.00'))
        elif fact.MesFactura:
            horas += Decimal(str(fact.MesFactura)) * hh.get('horas_mes', Decimal('0.00'))
        
        valor += Decimal(str(fact.Valor or '0'))
    
    return {'horas': horas, 'valor': valor}

# 5. Función para pendientes de facturación
def calcular_pendiente(anio: str, mes: str, cliente: Clientes, lineas: list, 
                      trabajado_actual: Decimal, facturado_actual: Decimal, 
                      horas_habiles: dict) -> dict:
    """Calcula pendientes de facturación con histórico del mes anterior"""
    try:
        mes_int = int(mes)
        anio_anterior = int(anio)
        mes_anterior = mes_int - 1
        
        if mes_anterior == 0:
            mes_anterior = 12
            anio_anterior -= 1
        
        # Normalizar mes anterior a formato de la base de datos
        mes_anterior_str = str(mes_anterior)
        
        # Obtener horas trabajadas del mes anterior 
        trabajado_anterior = Tiempos_Cliente.objects.filter(
            Anio=str(anio_anterior),
            Mes=mes_anterior_str,
            ClienteId=cliente.ClienteId,
            LineaId__in=lineas
        ).aggregate(total=Sum('Horas'))['total'] or Decimal('0.00')
        
        # Calcular pendiente
        pendiente_horas = (trabajado_anterior + trabajado_actual) - facturado_actual
        
        # Obtener tarifa cliente 
        tarifa = Tarifa_Clientes.objects.filter(
            clienteId=cliente.ClienteId,
            anio=int(anio),
            mes=int(mes)
        ).order_by('-id').first()
        
        # Calcular valor hora según tarifa
        tarifa_valor = Decimal('0.00')
        if tarifa:
            if tarifa.valorHora:
                tarifa_valor = tarifa.valorHora
            elif tarifa.valorDia:
                tarifa_valor = tarifa.valorDia / horas_habiles.get(mes, {}).get('horas_diarias', Decimal('1.00'))
            elif tarifa.valorMes:
                tarifa_valor = tarifa.valorMes / horas_habiles.get(mes, {}).get('horas_mes', Decimal('1.00'))
        
        return {
            'trabajado_anterior': trabajado_anterior,
            'horas': pendiente_horas,
            'valor': pendiente_horas * tarifa_valor
        }
    except Exception as e:
        print(f"Error calculando pendiente: {str(e)}")
        return {
            'trabajado_anterior': Decimal('0.00'),
            'horas': Decimal('0.00'),
            'valor': Decimal('0.00')
        }

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

def calcular_trabajado_por_linea(anio: str, mes: str, linea: Linea) -> Decimal:
    """Calcula horas trabajadas para una línea y mes específico"""
    return Tiempos_Cliente.objects.filter(
        Anio=anio, Mes=mes, LineaId=linea
    ).aggregate(total=Sum('Horas'))['total'] or Decimal('0.00')

def calcular_costo_por_linea(anio: str, mes: str, linea: Linea, horas_habiles: dict, clientes: list) -> Decimal:
    """Calcula costo total para una línea y mes específico sumando todos los clientes"""
    total = Decimal('0.00')
    for cliente in clientes:
        total += calcular_costo(anio, mes, cliente, [linea], horas_habiles)
    return total

def calcular_facturado_por_linea(anio: str, mes: str, linea: Linea, horas_habiles: dict, clientes: list) -> dict:
    """Calcula facturación total para una línea y mes específico sumando todos los clientes"""
    total_horas = Decimal('0.00')
    total_valor = Decimal('0.00')
    for cliente in clientes:
        facturado = calcular_facturado(anio, mes, cliente, [linea], horas_habiles)
        total_horas += facturado['horas']
        total_valor += facturado['valor']
    return {'horas': total_horas, 'valor': total_valor}

def calcular_pendiente_por_linea(anio: str, mes: str, linea: Linea, horas_habiles: dict, clientes: list) -> dict:
    """Calcula pendientes de facturación para una línea y mes específico sumando todos los clientes"""
    total_horas = Decimal('0.00')
    total_valor = Decimal('0.00')
    for cliente in clientes:
        trabajado_cliente = calcular_trabajado(anio, mes, cliente, [linea])
        facturado_cliente = calcular_facturado(anio, mes, cliente, [linea], horas_habiles)['horas']
        pendiente_cliente = calcular_pendiente(anio, mes, cliente, [linea], trabajado_cliente, facturado_cliente, horas_habiles)
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
    
    if form.is_valid():
        anio = form.cleaned_data['Anio']
        meses = [str(m) for m in form.cleaned_data['Mes']] if form.cleaned_data['Mes'] else [str(m) for m in range(1, 13)]
        lineas_seleccionadas = form.cleaned_data['LineaId'] or Linea.objects.all()
        clientes = form.cleaned_data['ClienteId'] or Clientes.objects.all()
        
        horas_habiles = obtener_horas_habiles(anio)
        resultados['conceptos'] = Concepto.objects.all()

        # Procesamiento general (existente)
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
                trabajado = calcular_trabajado(anio, mes, cliente, lineas_seleccionadas)
                costo = calcular_costo(anio, mes, cliente, lineas_seleccionadas, horas_habiles)
                facturado = calcular_facturado(anio, mes, cliente, lineas_seleccionadas, horas_habiles)
                pendiente = calcular_pendiente(
                    anio, mes, cliente, lineas_seleccionadas, 
                    trabajado, 
                    facturado['horas'],
                    horas_habiles
                )
                
                resultados['general'][mes]['Clientes'][cliente.Nombre_Cliente] = {
                    'Trabajado': trabajado,
                    'Costo': costo,
                    'Facturado': facturado,
                    'Pendiente': pendiente
                }
                resultados['general'][mes]['Clientes'][cliente.Nombre_Cliente]['Trabajado_Anterior'] = pendiente['trabajado_anterior']
                
                # Acumular totales generales
                for campo in ['Trabajado', 'Costo']:
                    resultados['totales'][cliente.Nombre_Cliente][campo] += resultados['general'][mes]['Clientes'][cliente.Nombre_Cliente][campo]
                
                for tipo in ['horas', 'valor']:
                    resultados['totales'][cliente.Nombre_Cliente][f'Facturado_{tipo}'] += facturado[tipo]
                    resultados['totales'][cliente.Nombre_Cliente][f'Pendiente_{tipo}'] += pendiente[tipo]
        
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

                trabajado = calcular_trabajado_por_linea(anio, mes, linea)
                costo = calcular_costo_por_linea(anio, mes, linea, horas_habiles, clientes)
                facturado = calcular_facturado_por_linea(anio, mes, linea, horas_habiles, clientes)
                pendiente = calcular_pendiente_por_linea(anio, mes, linea, horas_habiles, clientes)

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
                line_data['totales']['Pendiente_horas'] += pendiente['horas']
                line_data['totales']['Pendiente_valor'] += pendiente['valor']
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

    resultados['general'] = dict(resultados['general'])
    context = {
        'form': form,
        'resultados': resultados,
        'MESES': MESES,
        'Clientes': clientes if form.is_valid() else [],
        'Lineas': lineas_seleccionadas if form.is_valid() else [],
        'Conceptos': resultados['conceptos']
    }
    return render(request, 'Indicadores/indicadores_totales.html', context)