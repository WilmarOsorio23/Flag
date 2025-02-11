from decimal import Decimal
from django.db.models import FloatField, Sum, F, Value
from django.shortcuts import render
from django.db.models.functions import Coalesce
from collections import defaultdict

from Modulo.forms import Ind_Operatividad_FilterForm
from Modulo.models import Ind_Operat_Clientes, Ind_Operat_Conceptos, Horas_Habiles, Linea, Concepto

from plotly.offline import plot
import plotly.graph_objs as go


MESES = {
    '1': 'Ene', '2': 'Feb', '3': 'Mar', '4': 'Abr',
    '5': 'May', '6': 'Jun', '7': 'Jul', '8': 'Ago',
    '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'
}

def indicadores_operatividad_index(request):
    form = Ind_Operatividad_FilterForm(request.GET or None)
    conceptos = Concepto.objects.all()  # Obtener todos los conceptos
    context = {
        'form': form,
        'meses_disponibles': MESES.values(),
        'MESES': MESES,
        'conceptos': conceptos  # Pasar al contexto
    }

    if form.is_valid():
        cleaned_data = form.cleaned_data
        anio = cleaned_data.get('Anio')
        meses_seleccionados = cleaned_data.get('Mes')
        lineas_seleccionadas = cleaned_data.get('LineaId')

        # Validar que se haya seleccionado un año
        if not anio:
            return render(request, 'Indicadores/indicadores_operatividad_index.html', context)
        
        # Si no se selecciona ningún mes, mostrar todos los meses con datos para el año seleccionado
        if not meses_seleccionados:
            meses_seleccionados = ((Ind_Operat_Clientes.objects.filter(Anio=anio).values_list('Mes', flat=True).distinct()) or (Ind_Operat_Conceptos.objects.filter(Anio=anio).values_list('Mes', flat=True).distinct()))
            meses_seleccionados = [str(mes) for mes in meses_seleccionados]

        # Obtener datos base filtrados
        horas_habiles = obtener_horas_habiles(anio, meses_seleccionados)
        lineas = lineas_seleccionadas if lineas_seleccionadas else Linea.objects.all()
        
        resultados = []
        for linea in lineas:
            resultados_linea = procesar_linea(linea, anio, meses_seleccionados, horas_habiles, conceptos)
            resultados.append(resultados_linea)
        
        context.update({
            'resultados': resultados,
            'horas_habiles': horas_habiles,
            'total_horas': sum(h['total'] for h in horas_habiles.values()),
            'selected_anio': anio,
            'selected_mes': [str(m) for m in meses_seleccionados],
            'grafico_operacion': generar_grafico_no_operativos(resultados),
            'grafico_horas': generar_grafico_horas_linea(resultados)
        })

    return render(request, 'Indicadores/indicadores_operatividad_index.html', context)

def obtener_horas_habiles(anio, meses):
    registros = Horas_Habiles.objects.filter(Anio=anio, Mes__in=meses)
    
    # Crear un diccionario base con todos los meses solicitados en 0
    horas_habiles = {
        str(mes): {
            'dias': 0,
            'horas': 0.0,
            'total': 0.0
        } 
        for mes in meses
    }
    
    # Actualizar con los datos reales si existen
    for r in registros:
        mes_str = str(r.Mes)
        if mes_str in horas_habiles:
            horas_habiles[mes_str] = {
                'dias': r.Dias_Habiles,
                'horas': float(r.Horas_Laborales),
                'total': float(r.Dias_Habiles * r.Horas_Laborales)
            }
    
    return horas_habiles

def procesar_linea(linea, anio, meses, horas_habiles, conceptos):
    resultados_meses = defaultdict(dict)
    totales = defaultdict(float)
    totales_conceptos = defaultdict(float)  # Almacenar totales por concepto
    
    for mes in meses:
        # Obtener datos del mes con valores predeterminados
        clientes_mes = Ind_Operat_Clientes.objects.filter(
            Anio=anio, Mes=mes, LineaId=linea
        ).aggregate(
            trabajado=Coalesce(Sum('HorasTrabajadas', output_field=FloatField()), Value(0.0)),  # Usar FloatField
            facturable=Coalesce(Sum('HorasFacturables', output_field=FloatField()), Value(0.0))
        )
        
        conceptos_mes = Ind_Operat_Conceptos.objects.filter(
            Anio=anio, Mes=mes, LineaId=linea
        ).values('ConceptoId__Descripcion').annotate(
            total=Coalesce(Sum('HorasConcepto', output_field=FloatField()), Value(0.0))  # Usar FloatField
        )

        # Convertir conceptos_mes a un diccionario
        conceptos_dict = {c['ConceptoId__Descripcion']: c['total'] for c in conceptos_mes}

        # Inicializar todos los conceptos con 0 si no existen
        for concepto in conceptos:
            descripcion = concepto.Descripcion
            if descripcion not in conceptos_dict:
                conceptos_dict[descripcion] = 0.0
            totales_conceptos[descripcion] += conceptos_dict[descripcion]

        resultados_meses[mes]['Conceptos'] = conceptos_dict
        
        # Calcular indicadores
        horas_mes = horas_habiles.get(mes, {}).get('total', 1)
        recursos_asignados = (clientes_mes['trabajado'] or 0) + sum(conceptos_dict.values())
        resultados_meses[mes] = {
            'Recursos_asignados': safe_divide(recursos_asignados, horas_mes),
            'Recursos_activos': safe_divide(clientes_mes['trabajado'], horas_mes),
            'Capacidad': (safe_divide(recursos_asignados, horas_mes)) * horas_mes,
            'Trabajado': clientes_mes['trabajado'] or 0.0,
            'Facturable': clientes_mes['facturable'] or 0.0,
            'Tiempo_NO_facturable': ( clientes_mes['trabajado']) - (clientes_mes['facturable']) or 0.0,
            'Índ_de_oper': (safe_divide( clientes_mes['facturable'], (safe_divide(recursos_asignados, horas_mes)) * horas_mes))* 100 or 0.0,
            'Conceptos': conceptos_dict,
        }
        
        # Acumular totales
        for key in ['Trabajado', 'Facturable','Capacidad']:
            totales[key] += resultados_meses[mes][key] or 0  # Asegura que no sea None

        # Calcular nuevos campos
        suma_conceptos = sum(conceptos_dict.values())
        vacaciones = conceptos_dict.get('Vacaciones', 0)
        no_operativos = suma_conceptos - vacaciones
        total_fact_no_oper = (
            clientes_mes.get('facturable', 0) + 
            (clientes_mes.get('trabajado', 0) - clientes_mes.get('facturable', 0)) + 
            no_operativos
        )
        diferencia_horas = resultados_meses[mes].get('Capacidad', 0) - total_fact_no_oper

        # Almacenar en resultados_meses
        resultados_meses[mes].update({
            'Diferencia_recursos': safe_divide(suma_conceptos, horas_habiles[mes]['total']),
            'No_operativos': no_operativos,
            'Total_fact_no_oper': total_fact_no_oper,
            'Diferencia_horas': diferencia_horas,
        })

        # Acumular totales
        totales['suma_conceptos'] += suma_conceptos
        totales['suma_vacaciones'] += vacaciones
        totales['diferencia_recursos'] += resultados_meses[mes]['Diferencia_recursos']
        totales['no_operativos'] += no_operativos
        totales['total_fact_no_oper'] += total_fact_no_oper
        totales['diferencia_horas'] += diferencia_horas

    # Calcular totales finales
    return {
        'linea': linea.Linea,
        'meses': resultados_meses,
        'totales': {
            'Trabajado': totales['Trabajado'],
            'Facturable': totales['Facturable'],
            'Capacidad': totales['Capacidad'],
            'Conceptos': totales_conceptos,  # Pasar totales de conceptos
            'Tiempo_NO_facturable': totales['Trabajado'] - totales['Facturable'],
            'Índ_de_oper': safe_divide(totales['Facturable'], totales['Capacidad']) * 100,
            'Diferencia_recursos': totales['diferencia_recursos'],
            'No_operativos': totales['no_operativos'],
            'Total_fact_no_oper': totales['total_fact_no_oper'],
            'Diferencia_horas': totales['diferencia_horas'],
        }
    }

def safe_divide(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0:
        return 0
    return numerator / denominator

def generar_grafico_no_operativos(resultados):
    if not resultados:
        return ""

    # Lista para almacenar las gráficas y tablas de cada línea
    graficas_tablas = []

    # Colores para los meses (puedes ajustar los colores según prefieras)
    colores_meses = [
        'rgb(31, 119, 180)',  # Azul
        'rgb(255, 127, 14)',  # Naranja
        'rgb(44, 160, 44)',  # Verde
        'rgb(214, 39, 40)',  # Rojo
        'rgb(148, 103, 189)',  # Morado
        'rgb(140, 86, 75)',  # Marrón
        'rgb(227, 119, 194)',  # Rosa
        'rgb(127, 127, 127)',  # Gris
        'rgb(188, 189, 34)',  # Oliva
        'rgb(23, 190, 207)',  # Turquesa
    ]

    # Recorrer cada línea en los resultados
    for resultado in resultados:
        linea = resultado['linea']
        meses = list(resultado['meses'].keys())
        meses_nombres = [MESES.get(mes, mes) for mes in meses]  # Convertir números de mes a nombres

        # Obtener los conceptos y sus porcentajes por mes
        conceptos = set()
        datos_por_mes = defaultdict(dict)  # Usar un diccionario para almacenar los datos por mes

        for mes in meses:
            for concepto, horas in resultado['meses'][mes]['Conceptos'].items():
                conceptos.add(concepto)
                # Calcular el porcentaje de no operativos para cada concepto
                total_horas_mes = resultado['meses'][mes]['Capacidad']
                porcentaje = (horas / total_horas_mes) * 100 if total_horas_mes > 0 else 0
                datos_por_mes[mes][concepto] = porcentaje  # Almacenar en un diccionario

        # Ordenar los conceptos alfabéticamente
        conceptos_ordenados = sorted(conceptos)

        # Crear trazas para la gráfica
        data = []
        for i, mes in enumerate(meses):
            # Obtener los porcentajes para el mes actual
            porcentajes = [datos_por_mes[mes].get(concepto, 0) for concepto in conceptos_ordenados]

            # Crear una barra para cada mes
            data.append(go.Bar(
                x=conceptos_ordenados,
                y=porcentajes,
                name=meses_nombres[i],  # Nombre del mes
                marker_color=colores_meses[i % len(colores_meses)],  # Color del mes
                opacity=0.7
            ))

        # Layout de la gráfica
        layout = go.Layout(
            title=f"{linea} - Porcentaje No Operativos",
            xaxis=dict(title='Conceptos'),
            yaxis=dict(title='Porcentaje (%)'),
            barmode='group',
            legend=dict(orientation="h", x=0, y=-0.3),
            template="ggplot2",
            autosize=True,  # Nuevo parámetro
            margin=dict(
                l=50,
                r=50,
                b=100,
                t=100,
                pad=4,
                autoexpand=True
            )
        )

        # Crear la gráfica
        grafica = plot(
            {'data': data, 'layout': layout},
            output_type='div',
            include_plotlyjs=False,
            config={'responsive': True}
        )

        # Crear la tabla con los porcentajes por mes y concepto
        tabla = """
        <div class="table-responsive mt-4" style="overflow-x: auto;">
            <table class="table table-bordered" style="width: 100%;">
                <thead>
                    <tr>
                        <th>Concepto</th>
                        {}
                    </tr>
                </thead>
                <tbody>
                    {}
                </tbody>
            </table>
        </div>
        """.format(
            ''.join([f"<th>{mes}</th>" for mes in meses_nombres]),  # Encabezados de meses
            ''.join([
                f"<tr><td>{concepto}</td>" + ''.join([
                    f"<td>{round(datos_por_mes[mes].get(concepto, 0), 2)}%</td>" 
                    for mes in meses
                ]) + "</tr>"
                for concepto in conceptos_ordenados
            ])
        )

        # Combinar gráfica y tabla para esta línea
        graficas_tablas.append(grafica + tabla)

    # Unir todas las gráficas y tablas en un solo resultado
    return "<hr>".join(graficas_tablas)  # Separador entre gráficas de diferentes líneas


def generar_grafico_horas_linea(resultados):
    if not resultados:
        return ""

    # Lista para almacenar las gráficas y tablas de cada línea
    graficas_tablas = []

    # Colores para las barras y líneas
    colores = {
        'Capacidad': 'rgb(0, 0, 139)',  # Azul oscuro
        'Trabajado': 'rgb(50, 205, 50)',  # Verde lima
        'Facturable': 'rgb(0, 100, 0)',  # Verde oscuro
        'Índ_de_oper': 'rgb(255, 165, 0)',  # Naranja
        'Meta': 'rgb(255, 0, 0)'  # Rojo
    }

    # Recorrer cada línea en los resultados
    for resultado in resultados:
        # Obtener los meses seleccionados
        meses = list(resultado['meses'].keys())
        meses_nombres = [MESES.get(mes, mes) for mes in meses]  # Convertir números de mes a nombres

        # Extraer datos para la gráfica y la tabla
        capacidad_mes = [mes['Capacidad'] for mes in resultado['meses'].values()]
        trabajado_mes = [mes['Trabajado'] for mes in resultado['meses'].values()]
        facturable_mes = [mes['Facturable'] for mes in resultado['meses'].values()]
        ind_oper_mes = [mes['Índ_de_oper'] for mes in resultado['meses'].values()]
        meta_data = [90] * len(meses)  # Meta constante del 90%


        # Crear trazas para la gráfica
        data = [
            go.Bar(
                x=meses_nombres,
                y=capacidad_mes,
                name='Capacidad',
                marker_color=colores['Capacidad'],
                opacity=0.7,
                width=0.2  # Reducir el ancho de las barras
            ),
            go.Bar(
                x=meses_nombres,
                y=trabajado_mes,
                name='Trabajado',
                marker_color=colores['Trabajado'],
                opacity=0.7,
                width=0.2  # Reducir el ancho de las barras
            ),
            go.Bar(
                x=meses_nombres,
                y=facturable_mes,
                name='Facturable',
                marker_color=colores['Facturable'],
                opacity=0.7,
                width=0.2  # Reducir el ancho de las barras
            ),
            go.Scatter(
                x=meses_nombres,
                y=ind_oper_mes,
                name='Índice de Operación',
                line=dict(color=colores['Índ_de_oper'], width=4),  # Agrandar la línea
                mode='lines+markers',
                yaxis='y2'  # Usar el eje Y derecho
            ),
            go.Scatter(
                x=meses_nombres,
                y=meta_data,  # Meta constante del 90%
                name='Meta 90%',
                line=dict(color=colores['Meta'], dash='dash', width=3),  # Agrandar la línea
                mode='lines',
                yaxis='y2'  # Usar el eje Y derecho
            )
        ]

        # Layout de la gráfica
        layout = go.Layout(
            title=f"{resultado['linea']}",
            xaxis=dict(title='Meses', tickmode='array', tickvals=meses_nombres),
            yaxis=dict(title='Horas'),
            yaxis2=dict(
                title='Porcentaje (%)',
                overlaying='y',
                side='right',
                range=[0, 120],
                showgrid=False
            ),
            barmode='group',
            bargap=0.3,
            bargroupgap=0.1,
            legend=dict(orientation="h", x=0, y=-0.3),
            template="ggplot2",
            autosize=True,  # Nuevo parámetro
            margin=dict(autoexpand=True)  # Nuevo parámetro
        )

        # Crear la gráfica
        grafica = plot(
            {'data': data, 'layout': layout},
            output_type='div',
            include_plotlyjs=False
        )

        # Crear la tabla con cuadraditos de color
        tabla = """
        <div class="table-responsive mt-4" style="overflow-x: auto;">
            <table class="table table-bordered" style="width: 100%;">
                <thead>
                    <tr>
                        <th>Indicador</th>
                        {}
                    </tr>
                </thead>
                <tbody>
                    {}
                </tbody>
            </table>
        </div>
        """.format(
            ''.join([f"<th>{mes}</th>" for mes in meses_nombres]),  # Encabezados de meses
            ''.join([
                f"<tr><td><span style='display: inline-block; width: 12px; height: 12px; background-color: {colores['Capacidad']}; margin-right: 5px;'></span>Capacidad</td>" + ''.join([f"<td>{round(valor, 2)}</td>" for valor in capacidad_mes]) + "</tr>",
                f"<tr><td><span style='display: inline-block; width: 12px; height: 12px; background-color: {colores['Trabajado']}; margin-right: 5px;'></span>Trabajado</td>" + ''.join([f"<td>{round(valor, 2)}</td>" for valor in trabajado_mes]) + "</tr>",
                f"<tr><td><span style='display: inline-block; width: 12px; height: 12px; background-color: {colores['Facturable']}; margin-right: 5px;'></span>Facturable</td>" + ''.join([f"<td>{round(valor, 2)}</td>" for valor in facturable_mes]) + "</tr>",
                f"<tr><td><span style='display: inline-block; width: 12px; height: 12px; background-color: {colores['Índ_de_oper']}; margin-right: 5px;'></span>Índice de Operación</td>" + ''.join([f"<td>{round(valor, 2)}%</td>" for valor in ind_oper_mes]) + "</tr>",
                f"<tr><td><span style='display: inline-block; width: 12px; height: 12px; background-color: {colores['Meta']}; margin-right: 5px;'></span>Meta 90%</td>" + ''.join([f"<td>{valor}%</td>" for valor in meta_data]) + "</tr>"
            ])
        )

        # Combinar gráfica y tabla para esta línea
        graficas_tablas.append(grafica + tabla)

    # Unir todas las gráficas y tablas en un solo resultado
    return "<hr>".join(graficas_tablas)  # Separador entre gráficas de diferentes líneas