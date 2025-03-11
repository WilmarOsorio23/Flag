import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.db.models import Sum, F, FloatField
from decimal import Decimal
from django.db.models.functions import Coalesce
from collections import defaultdict
from Modulo.forms import Ind_Totales_FilterForm
from Modulo.models import (
    Horas_Habiles, Tarifa_Clientes, Tiempos_Cliente, FacturacionClientes,
    Nomina, Tarifa_Consultores, Linea, Clientes,
    TiemposConcepto, Concepto
)

MESES = {
    '1': 'Enero', '2': 'Febrero', '3': 'Marzo',
    '4': 'Abril', '5': 'Mayo', '6': 'Junio',
    '7': 'Julio', '8': 'Agosto', '9': 'Septiembre',
    '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
}

def indicadores_totales(request):
    form = Ind_Totales_FilterForm(request.GET or None)
    context = {'form': form, 'MESES': MESES}

    if form.is_valid():
        cleaned_data = form.cleaned_data
        anio = cleaned_data.get('Anio')
        meses_seleccionados = cleaned_data.get('Mes')
        lineas_seleccionadas = cleaned_data.get('LineaId')
        clientes_seleccionados = cleaned_data.get('ClienteId')

        if not anio:
            return render(request, 'Indicadores/indicadores_totales.html', context)

        horas_habiles = obtener_horas_habiles(anio, meses_seleccionados)
        
        resultados = {
            'general': {},
            'lineas_especiales': defaultdict(dict),
            'totales': defaultdict(float),
            'conceptos_no_fact': defaultdict(float)  # Initially a defaultdict
        }

        # Procesar cada mes
        for mes_str, mes_data in horas_habiles.items():
            datos_mes = procesar_mes(anio, mes_str, mes_data, clientes_seleccionados, lineas_seleccionadas)
            resultados['general'][mes_str] = datos_mes
            
            # Acumular totales generales
            for key in ['total_horas', 'total_costo', 'total_facturado', 'diferencia']:
                resultados['totales'][key] += datos_mes['totales_mes'][key]
            
            # Procesar líneas especiales
            for linea_nombre, datos_linea in datos_mes['lineas'].items():
                resultados['lineas_especiales'][linea_nombre][mes_str] = datos_linea
                
            # Conceptos no facturables
            for concepto, valor in datos_mes['conceptos_no_fact'].items():
                resultados['conceptos_no_fact'][concepto] += float(valor)

        # Convertir defaultdict a dict para el template
        resultados['conceptos_no_fact'] = dict(resultados['conceptos_no_fact'])  # Convert here

        # Calcular márgenes
        resultados['totales']['margen'] = calcular_margen(
            resultados['totales']['total_facturado'], 
            resultados['totales']['total_costo']
        )

        context['resultados'] = resultados
        context.update({
            'selected_anio': anio,
            'selected_meses': [str(m) for m in meses_seleccionados] if meses_seleccionados else [],
            'selected_lineas': lineas_seleccionadas,
            'selected_clientes': clientes_seleccionados,
        })

    return render(request, 'Indicadores/indicadores_totales.html', context)

def obtener_horas_habiles(anio, meses):
    registros = Horas_Habiles.objects.filter(Anio=anio)
    if meses:
        registros = registros.filter(Mes__in=meses)
    
    return {
        str(r.Mes): {
            'dias': r.Dias_Habiles,
            'horas': float(r.Horas_Laborales),
            'total': float(r.Dias_Habiles * r.Horas_Laborales)
        }
        for r in registros
    }

def procesar_mes(anio, mes, mes_obj, clientes, lineas):
    datos_mes = {
        'dias': mes_obj['dias'],
        'horas_totales': mes_obj['total'],
        'clientes': {},
        'totales_mes': defaultdict(float),
        'lineas': defaultdict(lambda: {
            'trabajado': 0.0,
            'costo': 0.0,
            'facturado': 0.0,
            'pendiente_horas': 0.0,
            'pendiente_valor': 0.0,
            'diferencia': 0.0,
            'margen': 0.0
        }),
        'conceptos_no_fact': obtener_conceptos_no_facturables(anio, mes)
    }

    # Procesar clientes
    clientes_query = Clientes.objects.filter(Activo=True)
    if clientes:
        clientes_query = clientes_query.filter(id__in=[c.id for c in clientes])
    if lineas:
        clientes_query = clientes_query.filter(linea__in=lineas)

    for cliente in clientes_query:
        # Datos básicos
        horas_trabajadas = Tiempos_Cliente.objects.filter(
            Anio=anio, Mes=mes, ClienteId=cliente
        ).aggregate(total=Coalesce(Sum('Horas', output_field=FloatField()), 0.0))['total']

        costos = calcular_costos(cliente, anio, mes, horas_trabajadas)
        facturado = obtener_facturado(cliente, anio, mes)
        pendiente = calcular_pendientes(anio, mes, cliente, horas_trabajadas, facturado['horas'])

        # Obtener líneas asociadas al cliente desde FacturacionClientes
        facturaciones = FacturacionClientes.objects.filter(
            Anio=anio, 
            Mes=mes, 
            ClienteId=cliente
        ).select_related('LineaId')
        
        # Almacenar datos del cliente
        datos_mes['clientes'][cliente.Nombre_Cliente] = {
            'trabajado': float(horas_trabajadas),
            'costo': float(costos['total']),
            'facturado': {
                'horas': float(facturado['horas']),
                'valor': float(facturado['valor'])
            },
            'pendiente': {
                'horas': float(pendiente['horas']),
                'valor': float(pendiente['valor'])
            }
        }
        
        cliente_data = datos_mes['clientes'][cliente.Nombre_Cliente]
        datos_mes['totales_mes']['total_horas'] += cliente_data['trabajado']
        datos_mes['totales_mes']['total_costo'] += cliente_data['costo']
        datos_mes['totales_mes']['total_facturado'] += cliente_data['facturado']['valor']
        
        # Procesar por cada línea en las facturaciones del cliente
        for factura in facturaciones:
            linea = factura.LineaId
            linea_nombre = linea.Linea if linea else 'Sin Línea'

            # Acumular datos por línea
            datos_mes['lineas'][linea_nombre]['trabajado'] += horas_trabajadas
            datos_mes['lineas'][linea_nombre]['costo'] += costos['total']
            datos_mes['lineas'][linea_nombre]['facturado'] += facturado['valor']
            datos_mes['lineas'][linea_nombre]['pendiente_horas'] += pendiente['horas']
            datos_mes['lineas'][linea_nombre]['pendiente_valor'] += pendiente['valor']

    # Calcular diferencias y márgenes para líneas
    for linea in datos_mes['lineas'].values():
        linea['diferencia'] = linea['facturado'] - linea['costo']
        linea['margen'] = calcular_margen(linea['facturado'], linea['costo'])

    # Calcular diferencia total
    datos_mes['totales_mes']['diferencia'] = (
        datos_mes['totales_mes']['total_facturado'] - 
        datos_mes['totales_mes']['total_costo']
    )

    return datos_mes

def calcular_costos(cliente, anio, mes, horas):
    nominas = Nomina.objects.filter(Anio=anio, Mes=mes, Cliente=cliente)
    costo_empleados = sum(
        float(n.Salario) / float(n.Cliente.horas_mes) * float(horas)
        for n in nominas
    )
    
    tarifas = Tarifa_Consultores.objects.filter(anio=anio, mes=mes, clienteID=cliente)
    costo_consultores = sum(float(t.valorHora) * float(horas) for t in tarifas)
    
    return {
        'empleados': float(costo_empleados),
        'consultores': float(costo_consultores),
        'total': float(costo_empleados + costo_consultores)
    }


def obtener_facturado(cliente, anio, mes):
    facturacion = FacturacionClientes.objects.filter(
        Anio=anio, Mes=mes, ClienteId=cliente
    ).aggregate(
        horas=Coalesce(Sum('HorasFactura'), 0.0),
        valor=Coalesce(Sum('Valor'), 0.0)
    )
    return {
        'horas': float(facturacion['horas']),
        'valor': float(facturacion['valor'])
    }

def calcular_margen(facturado, costo):
    try:
        return ((facturado - costo) / costo) * 100
    except ZeroDivisionError:
        return 0.0

# Añade al final del archivo views.py
def calcular_totales_mes(datos_clientes):
    totales = {
        'total_horas': 0.0,
        'total_costo': 0.0,
        'total_facturado': 0.0,
        'diferencia': 0.0
    }
    
    for cliente in datos_clientes.values():
        totales['total_horas'] += float(cliente['trabajado'])
        totales['total_costo'] += float(cliente['costo'])
        totales['total_facturado'] += float(cliente['facturado']['valor'])
    
    totales['diferencia'] = totales['total_facturado'] - totales['total_costo']
    return totales

def calcular_totales_generales(datos_general):
    totales = {
        'total_horas_anio': 0.0,
        'total_costo_anio': 0.0,
        'total_facturado_anio': 0.0,
        'diferencia_anio': 0.0
    }
    
    for mes in datos_general.values():
        totales['total_horas_anio'] += float(mes['totales_mes']['total_horas'])
        totales['total_costo_anio'] += float(mes['totales_mes']['total_costo'])
        totales['total_facturado_anio'] += float(mes['totales_mes']['total_facturado'])
    
    totales['diferencia_anio'] = totales['total_facturado_anio'] - totales['total_costo_anio']
    return totales

def obtener_conceptos_no_facturables(anio, mes):
    tiempos_conceptos = TiemposConcepto.objects.filter(
        Anio=anio, 
        Mes=mes
    ).values('ConceptoId__Descripcion').annotate(
        total_horas=Sum('Horas')
    )
    
    return {
        item['ConceptoId__Descripcion']: float(item['total_horas'] or 0)
        for item in tiempos_conceptos
    }

def procesar_linea(linea, anio, meses_data):
    resultados_linea = {}
    
    for mes_obj in meses_data:
        mes = str(mes_obj.Mes)
        resultados_linea[mes] = {
            'horas_trabajadas': Tiempos_Cliente.objects.filter(
                Anio=anio, Mes=mes, ClienteId__linea=linea
            ).aggregate(total=Coalesce(Sum('Horas', output_field=FloatField()), 0.0))['total'],
            'costos': Nomina.objects.filter(
                Anio=anio, Mes=mes, ClienteId__linea=linea
            ).aggregate(total=Coalesce(Sum('Salario', output_field=FloatField()), 0.0))['total']
        }
    
    return resultados_linea

def calcular_pendientes(anio, mes, cliente, horas_trabajadas, facturado_horas):
    try:
        anio = int(anio)
        mes = int(mes)
    except (ValueError, TypeError):
        return {'horas': 0.0, 'valor': 0.0}
    
    if mes == 1:
        mes_anterior = 12
        anio_anterior = anio - 1
    else:
        mes_anterior = mes - 1
        anio_anterior = anio

    horas_anterior = Tiempos_Cliente.objects.filter(
        Anio=anio_anterior,
        Mes=mes_anterior,
        ClienteId=cliente
    ).aggregate(
        total=Coalesce(Sum('Horas'), 0.0, output_field=FloatField())
    )['total'] or 0.0

    facturado_anterior = FacturacionClientes.objects.filter(
        Anio=anio_anterior,
        Mes=mes_anterior,
        ClienteId=cliente
    ).aggregate(
        total=Coalesce(Sum('HorasFactura'), 0.0, output_field=FloatField())
    )['total'] or 0.0

    pendiente_horas = max(horas_anterior - facturado_anterior, 0.0)
    pendiente_valor = pendiente_horas * obtener_valor_hora_cliente(cliente, anio_anterior, mes_anterior)

    return {
        'horas': pendiente_horas,
        'valor': pendiente_valor
    }

def obtener_valor_hora_cliente(cliente, anio, mes):
    try:
        anio_int = int(anio)
        mes_int = int(mes)
    except (ValueError, TypeError):
        return 0.0
    
    tarifa = Tarifa_Clientes.objects.filter(
        clienteId=cliente,
        anio=anio_int,
        mes=mes_int
    ).first()
    
    if tarifa and tarifa.valorHora is not None:
        return float(tarifa.valorHora)
    else:
        try:
            horas_habiles = Horas_Habiles.objects.get(Anio=anio_int, Mes=mes_int)
            total_horas_mes = float(horas_habiles.Horas_Laborales)
        except Horas_Habiles.DoesNotExist:
            total_horas_mes = 0.0
        
        salario_total = Nomina.objects.filter(
            Cliente=cliente,
            Anio=anio_int,
            Mes=mes_int
        ).aggregate(
            total=Coalesce(Sum('Salario'), 0.0, output_field=FloatField())
        )['total'] or 0.0
        
        if total_horas_mes > 0:
            return float(salario_total) / total_horas_mes
        else:
            return 0.0