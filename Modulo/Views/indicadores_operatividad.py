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

from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_clientes')

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

        # Verificar si hay resultados antes de generar gráficos
        if resultados:
            context.update({
                'resultados': resultados,
                'horas_habiles': horas_habiles,
                'total_horas': sum(h['total'] for h in horas_habiles.values()),
                'selected_anio': anio,
                'selected_mes': [str(m) for m in meses_seleccionados],
                'grafico_operacion': generar_grafico_no_operativos(resultados),
                'grafico_horas': generar_grafico_horas_linea(resultados)
            })
        else:
            context.update({
                'resultados': [],
                'horas_habiles': horas_habiles,
                'total_horas': 0,
                'selected_anio': anio,
                'selected_mes': [str(m) for m in meses_seleccionados],
                'grafico_operacion': "<p>No hay datos para generar el gráfico de no operativos.</p>",
                'grafico_horas': "<p>No hay datos para generar el gráfico de horas.</p>"
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

        # Obtener valores de Vacaciones y Día de la Familia
        vacaciones = conceptos_dict.get('Vacaciones', 0)
        dia_familia = conceptos_dict.get('Dia de la Familia', 0)
        
        recursos_asignados = ((clientes_mes['trabajado'] or 0) + sum(conceptos_dict.values()))

        # 1. Restar Vacaciones y Día de la Familia del total de la capacidad
        capacidad_ajustada = ((safe_divide(recursos_asignados, horas_mes)) * horas_mes) - vacaciones - dia_familia

        # 2. Restar Día de la Familia de NO operativos
        no_operativos = sum(conceptos_dict.values()) - vacaciones - dia_familia

        resultados_meses[mes] = {
            'Recursos_asignados': safe_divide((recursos_asignados - vacaciones), horas_mes),
            'Recursos_activos': safe_divide(clientes_mes['trabajado'], horas_mes),
            'Capacidad': capacidad_ajustada,
            'Trabajado': clientes_mes['trabajado'] or 0.0,
            'Facturable': clientes_mes['facturable'] or 0.0,
            'Tiempo_NO_facturable': ( clientes_mes['trabajado']) - (clientes_mes['facturable']) or 0.0,
            'Índ_de_oper': safe_divide( clientes_mes['facturable'],capacidad_ajustada)* 100 or 0.0,
            'Conceptos': conceptos_dict,
        }
        
        # Acumular totales
        for key in ['Trabajado', 'Facturable','Capacidad']:
            totales[key] += resultados_meses[mes][key] or 0  # Asegura que no sea None

        # Calcular nuevos campos
        suma_conceptos = sum(conceptos_dict.values())
        vacaciones = conceptos_dict.get('Vacaciones', 0)
        no_operativos = sum(conceptos_dict.values()) - vacaciones - dia_familia
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
        return "<p>No hay datos para generar el gráfico de no operativos.</p>"

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
        # Verificar si hay meses procesados para esta línea
        if not resultado['meses']:
            continue

        linea = resultado['linea']
        meses = list(resultado['meses'].keys())
        meses_nombres = [MESES.get(mes, mes) for mes in meses]  # Convertir números de mes a nombres

        # Recopilar datos y verificar si hay valores válidos
        conceptos = set()
        datos_por_mes = defaultdict(dict)
        has_valid_data = False  # Bandera para datos válidos

        for mes in meses:
            mes_data = resultado['meses'][mes]
            for concepto, horas in mes_data['Conceptos'].items():
                # Calcular porcentaje solo si hay capacidad
                total_horas_mes = mes_data.get('Capacidad', 0)
                porcentaje = 0
                if total_horas_mes > 0 and horas > 0:
                    porcentaje = (horas / total_horas_mes) * 100
                    has_valid_data = True  # Hay al menos un dato válido
                
                conceptos.add(concepto)
                datos_por_mes[mes][concepto] = porcentaje

        # Saltar si no hay datos válidos
        if not has_valid_data:
            continue

        # Ordenar los conceptos alfabéticamente
        conceptos_ordenados = sorted(conceptos)

        # Verificar si hay datos para graficar
        if not conceptos_ordenados:
            continue  # Saltar si no hay conceptos

        # Crear trazas para la gráfica
        data = []
        for i, mes in enumerate(meses):
            # Obtener los porcentajes para el mes actual
            porcentajes = [datos_por_mes[mes].get(concepto, 0) for concepto in conceptos_ordenados]

            # Saltar meses con todos los porcentajes en cero
            if sum(porcentajes) == 0:
                continue

            # Crear una barra para cada mes
            data.append(go.Bar(
                x=conceptos_ordenados,
                y=porcentajes,
                name=meses_nombres[i],  # Nombre del mes
                marker_color=colores_meses[i % len(colores_meses)],  # Color del mes
                opacity=0.7
            ))

        # Verificar si hay datos en `data`
        if not data:
            continue  # Saltar si no hay datos

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

        try:
            grafica = plot(
                {'data': data, 'layout': layout},
                output_type='div',
                include_plotlyjs=False,
                config={'responsive': True}
            )
        except Exception as e:
            print(f"Error al generar gráfico: {str(e)}")
            continue

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
    return "<hr>".join(graficas_tablas) if graficas_tablas else "<p>No hay datos para generar el gráfico de no operativos.</p>"

def generar_grafico_horas_linea(resultados):
    if not resultados:
        return "<p>No hay datos para generar el gráfico de horas.</p>"

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
        # Verificar si hay meses procesados para esta línea
        if not resultado['meses']:
            continue  # Saltar si no hay datos

        # Obtener los meses seleccionados
        meses = list(resultado['meses'].keys())
        meses_nombres = [MESES.get(mes, mes) for mes in meses]  # Convertir números de mes a nombres

        # Extraer datos y manejar valores nulos o faltantes
        capacidad_mes = []
        trabajado_mes = []
        facturable_mes = []
        ind_oper_mes = []

        for mes in meses:
            mes_data = resultado['meses'][mes]
            capacidad_mes.append(mes_data.get('Capacidad', 0))
            trabajado_mes.append(mes_data.get('Trabajado', 0))
            facturable_mes.append(mes_data.get('Facturable', 0))
            ind_oper = mes_data.get('Índ_de_oper', 0)
            ind_oper_mes.append(ind_oper if ind_oper is not None else 0)

        # Verificar si hay datos para graficar
        if (
            sum(capacidad_mes) == 0
            and sum(trabajado_mes) == 0
            and sum(facturable_mes) == 0
        ):
            continue  # Saltar si todos los valores son cero

        meta_data = [90] * len(meses)  # Meta constante del 90%

        # Crear trazas solo si hay datos
        data = []
        if any(capacidad_mes):
            data.append(
                go.Bar(
                    x=meses_nombres,
                    y=capacidad_mes,
                    name='Capacidad',
                    marker_color=colores['Capacidad'],
                    opacity=0.7,
                    width=0.2
                )
            )
        if any(trabajado_mes):
            data.append(
                go.Bar(
                    x=meses_nombres,
                    y=trabajado_mes,
                    name='Trabajado',
                    marker_color=colores['Trabajado'],
                    opacity=0.7,
                    width=0.2
                )
            )
        if any(facturable_mes):
            data.append(
                go.Bar(
                    x=meses_nombres,
                    y=facturable_mes,
                    name='Facturable',
                    marker_color=colores['Facturable'],
                    opacity=0.7,
                    width=0.2
                )
            )
        if any(ind_oper_mes):
            data.append(
                go.Scatter(
                    x=meses_nombres,
                    y=ind_oper_mes,
                    name='Índice de Operación',
                    line=dict(color=colores['Índ_de_oper'], width=4),
                    mode='lines+markers',
                    yaxis='y2'
                )
            )

        # Siempre agregar la meta
        data.append(
            go.Scatter(
                x=meses_nombres,
                y=meta_data,
                name='Meta 90%',
                line=dict(color=colores['Meta'], dash='dash', width=3),
                mode='lines',
                yaxis='y2'
            )
        )

        # Crear gráfico solo si hay trazas
        if not data:
            continue

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
    return "<hr>".join(graficas_tablas) if graficas_tablas else "<p>No hay datos para el gráfico de horas.</p>"