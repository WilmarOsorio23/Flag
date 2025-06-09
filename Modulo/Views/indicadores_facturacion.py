from django.shortcuts import render
from django.db.models import Sum, F, Q, Case, When, Value, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from ..models import (
    Linea, Tiempos_Cliente, TiemposConcepto, FacturacionClientes,
    Horas_Habiles
)
from ..forms import Ind_Facturacion_FilterForm
import json

def obtener_horas_habiles(anio: str) -> dict:
    """Obtiene las horas hábiles por mes para un año específico"""
    horas_habiles = {}
    registros = Horas_Habiles.objects.filter(Anio=anio)
    for registro in registros:
        horas_habiles[registro.Mes] = registro.Horas_Laborales
    return horas_habiles

def calcular_trabajado(linea_id: int, anio: str, mes: str) -> Decimal:
    """Calcula las horas trabajadas para una línea en un mes específico"""
    # Horas trabajadas en clientes
    horas_clientes = Tiempos_Cliente.objects.filter(
        LineaId=linea_id,
        Anio=anio,
        Mes=mes
    ).aggregate(
        total=Coalesce(Sum('Horas'), Decimal('0'))
    )['total']

    # Horas trabajadas en conceptos
    horas_conceptos = TiemposConcepto.objects.filter(
        LineaId=linea_id,
        Anio=anio,
        Mes=mes
    ).aggregate(
        total=Coalesce(Sum('Horas'), Decimal('0'))
    )['total']

    return horas_clientes + horas_conceptos

def calcular_facturable(linea_id: int, anio: str, mes: str) -> Decimal:
    """Calcula las horas facturables para una línea en un mes específico"""
    return Tiempos_Cliente.objects.filter(
        LineaId=linea_id,
        Anio=anio,
        Mes=mes
    ).aggregate(
        total=Coalesce(Sum('Horas'), Decimal('0'))
    )['total']

def calcular_facturado(linea_id: int, anio: str, mes: str) -> Decimal:
    """Calcula las horas facturadas para una línea en un mes específico"""
    return FacturacionClientes.objects.filter(
        LineaId=linea_id,
        Anio=anio,
        Mes=mes
    ).aggregate(
        total=Coalesce(Sum('HorasFactura'), Decimal('0'))
    )['total']

def calcular_indicadores_linea(linea: Linea, anio: str, meses: list) -> dict:
    """Calcula todos los indicadores para una línea específica"""
    resultados = {
        'nombre': linea.Linea,
        'meses': {},
        'totales': {
            'trabajado': Decimal('0'),
            'facturable': Decimal('0'),
            'facturado': Decimal('0'),
            'ind_fact': Decimal('0'),
            'meta': Decimal('90'),
            'pend_fact': Decimal('0'),
            'no_facturable': Decimal('0')
        }
    }

    for mes in meses:
        trabajado = calcular_trabajado(linea.LineaId, anio, mes)
        facturable = calcular_facturable(linea.LineaId, anio, mes)
        facturado = calcular_facturado(linea.LineaId, anio, mes)
        
        # Cálculo de indicadores
        ind_fact = (facturado / facturable * 100) if facturable else Decimal('0')
        pend_fact = trabajado - facturado
        no_facturable = trabajado - facturable

        resultados['meses'][mes] = {
            'trabajado': trabajado,
            'facturable': facturable,
            'facturado': facturado,
            'ind_fact': ind_fact,
            'meta': Decimal('90'),
            'pend_fact': pend_fact,
            'no_facturable': no_facturable
        }

        # Actualizar totales
        resultados['totales']['trabajado'] += trabajado
        resultados['totales']['facturable'] += facturable
        resultados['totales']['facturado'] += facturado

    # Calcular totales finales
    total_facturable = resultados['totales']['facturable']
    total_facturado = resultados['totales']['facturado']
    total_trabajado = resultados['totales']['trabajado']

    resultados['totales']['ind_fact'] = (total_facturado / total_facturable * 100) if total_facturable else Decimal('0')
    resultados['totales']['pend_fact'] = total_facturado - total_trabajado
    resultados['totales']['no_facturable'] = total_trabajado - total_facturable

    return resultados

def generar_grafico_facturacion(resultados: list) -> dict:
    """Genera los datos para el gráfico de facturación"""
    datos_grafico = {
        'labels': [],
        'datasets': [
            {
                'label': 'Trabajado',
                'data': [],
                'type': 'bar'
            },
            {
                'label': 'Facturable',
                'data': [],
                'type': 'bar'
            },
            {
                'label': 'Facturado',
                'data': [],
                'type': 'bar'
            },
            {
                'label': 'Índ.Fact',
                'data': [],
                'type': 'line',
                'yAxisID': 'porcentaje'
            },
            {
                'label': 'Meta 90%',
                'data': [],
                'type': 'line',
                'yAxisID': 'porcentaje'
            }
        ]
    }

    for linea in resultados:
        datos_grafico['labels'].append(linea['nombre'])
        datos_grafico['datasets'][0]['data'].append(float(linea['totales']['trabajado']))
        datos_grafico['datasets'][1]['data'].append(float(linea['totales']['facturable']))
        datos_grafico['datasets'][2]['data'].append(float(linea['totales']['facturado']))
        datos_grafico['datasets'][3]['data'].append(float(linea['totales']['ind_fact']))
        datos_grafico['datasets'][4]['data'].append(90)  # Meta constante

    return datos_grafico

def indicadores_facturacion(request):
    """Vista principal para el indicador de facturación"""
    if request.method == 'POST':
        form = Ind_Facturacion_FilterForm(request.POST)
        if form.is_valid():
            anio = form.cleaned_data['Anio']
            meses_seleccionados = form.cleaned_data['Mes']
            lineas_seleccionadas = form.cleaned_data['LineaId']

            # Si no se seleccionan meses, usar todos
            if not meses_seleccionados:
                meses_seleccionados = [str(i) for i in range(1, 13)]

            # Si no se seleccionan líneas, usar todas
            if not lineas_seleccionadas:
                lineas_seleccionadas = Linea.objects.all()

            resultados = []
            for linea in lineas_seleccionadas:
                resultado_linea = calcular_indicadores_linea(linea, anio, meses_seleccionados)
                resultados.append(resultado_linea)

            datos_grafico = generar_grafico_facturacion(resultados)

            return render(request, 'Indicadores/indicadores_facturacion.html', {
                'form': form,
                'resultados': resultados,
                'datos_grafico': json.dumps(datos_grafico),
                'meses_seleccionados': sorted(meses_seleccionados, key=int),
                'anio': anio
            })
    else:
        form = Ind_Facturacion_FilterForm()
        
    return render(request, 'Indicadores/indicadores_facturacion.html', {
        'form': form
    }) 