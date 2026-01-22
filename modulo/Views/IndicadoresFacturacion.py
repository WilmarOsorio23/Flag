from django.shortcuts import render
from django.db.models import Sum, F, Q, Case, When, Value, DecimalField, FloatField
from django.db.models.functions import Coalesce
from decimal import Decimal
from modulo.models import (
    Ind_Operat_Clientes, Linea, Tiempos_Cliente, TiemposConcepto, FacturacionClientes,
    Horas_Habiles
)
from modulo.forms import Ind_Facturacion_FilterForm
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
import traceback

MESES = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
    5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}

from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

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
        total=Coalesce(Sum('Horas'), Decimal('0'), output_field=DecimalField())
    )['total'] or Decimal('0')

    return horas_clientes

def calcular_facturable(linea_id: int, anio: str, mes: str) -> Decimal:
    """Calcula las horas facturables para una línea en un mes específico"""
    return Ind_Operat_Clientes.objects.filter(
        LineaId=linea_id,
        Anio=anio,
        Mes=mes
    ).aggregate(
        total=Coalesce(Sum('HorasFacturables'), Decimal('0'), output_field=DecimalField())
    )['total'] or Decimal('0')

def calcular_facturado(linea_id: int, anio: str, mes: str) -> Decimal:
    """Calcula las horas facturadas para una línea en un mes específico"""
    return FacturacionClientes.objects.filter(
        LineaId=linea_id,
        Anio=anio,
        Mes=mes
    ).aggregate(
        total=Coalesce(Sum('HorasFactura'), Decimal('0'), output_field=DecimalField())
    )['total'] or Decimal('0')

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

    for mes_str in meses:
        mes_int = int(mes_str)
        trabajado = calcular_trabajado(linea.LineaId, anio, mes_str)
        facturable = calcular_facturable(linea.LineaId, anio, mes_str)
        facturado = calcular_facturado(linea.LineaId, anio, mes_str)
        
        # Cálculo de indicadores
        ind_fact = (facturado / facturable * Decimal('100')) if facturable and facturable != Decimal('0') else Decimal('0')
        pend_fact = trabajado - facturado
        no_facturable = trabajado - facturable

        # Usar el entero como clave
        resultados['meses'][mes_int] = {
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

    # Manejar división por cero
    resultados['totales']['ind_fact'] = (total_facturado / total_facturable * Decimal('100')) if total_facturable and total_facturable != Decimal('0') else Decimal('0')
    resultados['totales']['pend_fact'] = total_facturado - total_trabajado
    resultados['totales']['no_facturable'] = total_trabajado - total_facturable

    return resultados

def generar_graficos_por_linea(resultados, meses_seleccionados, meses_nombres):
    """Genera datos para gráficos por línea y mes"""
    graficos = []
    
    for resultado in resultados:
        trabajado_data = []
        facturable_data = []
        facturado_data = []
        ind_fact_data = []

        for mes_int in meses_seleccionados:
            try:
                mes_info = resultado['meses'][mes_int]
                
                trab_val = mes_info.get('trabajado', Decimal('0'))
                fact_val = mes_info.get('facturable', Decimal('0'))
                facd_val = mes_info.get('facturado', Decimal('0'))
                ind_val = mes_info.get('ind_fact', Decimal('0'))

                trabajado_data.append(float(trab_val))
                facturable_data.append(float(fact_val))
                facturado_data.append(float(facd_val))
                ind_fact_data.append(float(ind_val))
            except Exception as e:
                traceback.print_exc()
                trabajado_data.append(0.0)
                facturable_data.append(0.0)
                facturado_data.append(0.0)
                ind_fact_data.append(0.0)
                continue


        datos_grafico = {
            'nombre': resultado['nombre'],
            'labels': meses_nombres,
            'datasets': [
                {
                    'label': 'Trabajado',
                    'data': trabajado_data,
                    'type': 'bar',
                    'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Facturable',
                    'data': facturable_data,
                    'type': 'bar',
                    'backgroundColor': 'rgba(75, 192, 192, 0.5)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Facturado',
                    'data': facturado_data,
                    'type': 'bar',
                    'backgroundColor': 'rgba(153, 102, 255, 0.5)',
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Índ.Fact',
                    'data': ind_fact_data,
                    'type': 'line',
                    'yAxisID': 'y1',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 2,
                    'fill': False
                },
                {
                    'label': 'Meta 90%',
                    'data': [90] * len(meses_seleccionados),
                    'type': 'line',
                    'yAxisID': 'y1',
                    'borderColor': 'rgba(255, 159, 64, 1)',
                    'borderWidth': 2,
                    'borderDash': [5, 5],
                    'fill': False
                }
            ]
        }
        graficos.append(datos_grafico)
    
    return graficos

@login_required
@verificar_permiso('can_view_indicadores_facturacion')
def indicadores_facturacion(request):
    """Vista principal para el indicador de facturación"""
    try:
        if request.method == 'POST':
            form = Ind_Facturacion_FilterForm(request.POST)
            if form.is_valid():
                anio = form.cleaned_data['Anio']
                meses_seleccionados = form.cleaned_data['Mes']
                lineas_seleccionadas = form.cleaned_data['LineaId']

                if not meses_seleccionados:
                    meses_seleccionados = [str(i) for i in range(1, 13)]
                
                meses_seleccionados_ints = sorted([int(m) for m in meses_seleccionados])
                meses_nombres = [MESES[m] for m in meses_seleccionados_ints]

                if not lineas_seleccionadas:
                    lineas_seleccionadas = Linea.objects.all()

                resultados = []
                for linea in lineas_seleccionadas:
                    resultado_linea = calcular_indicadores_linea(
                        linea, anio, [str(m) for m in meses_seleccionados_ints]
                    )
                    resultados.append(resultado_linea)

                graficos_por_linea = generar_graficos_por_linea(
                    resultados, 
                    meses_seleccionados_ints, 
                    meses_nombres
                )
                
                return render(request, 'Indicadores/IndicadoresFacturacion.html', {
                    'form': form,
                    'resultados': resultados,
                    'graficos_por_linea': graficos_por_linea,
                    'meses_seleccionados': meses_seleccionados_ints,
                    'meses_nombres': meses_nombres,
                    'anio': anio
                })
        else:
            form = Ind_Facturacion_FilterForm()
            graficos_por_linea = []
            resultados = []
            meses_seleccionados_ints = []
            meses_nombres = []
            anio = None
            
        return render(request, 'Indicadores/IndicadoresFacturacion.html', {
            'form': form,
            'graficos_por_linea': graficos_por_linea,
            'resultados': resultados,
            'meses_seleccionados': meses_seleccionados_ints,
            'meses_nombres': meses_nombres,
            'anio': anio
        })

    except Exception as e:
        print(f"Error: {e}\n{traceback.format_exc()}")
        return HttpResponse(f"<h1>Error en la vista</h1><pre>{e}</pre><pre>{traceback.format_exc()}</pre>")