from decimal import Decimal
from django.shortcuts import render
from Modulo.models import FacturacionClientes, Linea
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from datetime import datetime
from Modulo.forms import FacturacionClientesFilterForm
from django.db.models import Sum
from collections import defaultdict

def filtrar_datos(form=None):
    facturas = FacturacionClientes.objects.all().select_related(
        'LineaId', 'ModuloId', 'ClienteId'
    )

    if form and form.is_valid():
        anio = form.cleaned_data.get('Anio')
        lineas = form.cleaned_data.get('LineaId')
        meses = form.cleaned_data.get('Mes')
        ceco = form.cleaned_data.get('Ceco')

        print(f"\nFiltros aplicados:")
        print(f"Año: {anio}")
        print(f"Líneas: {lineas}")
        print(f"Meses: {meses}")
        print(f"Ceco: {ceco}\n")

        if anio:
            facturas = facturas.filter(Anio=anio)
        if lineas:
            facturas = facturas.filter(LineaId__in=lineas)
        if meses:
            facturas = facturas.filter(Mes__in=[int(m) for m in meses])
        if ceco:
            facturas = facturas.filter(Ceco__icontains=ceco)

    # Imprimir consulta SQL generada
    print("Consulta SQL:", facturas.query)
    
    facturas_agrupadas = facturas.values(
        'ConsecutivoId',
        'Mes', 
        'Ceco',
        'LineaId__Linea',
        'ModuloId__Modulo',
        'Descripcion'
    ).annotate(
        total_valor=Sum('Valor')
    ).order_by('Ceco', 'LineaId__Linea', 'ModuloId__Modulo', 'Mes')

    # Verificar conteo antes y después del agrupamiento
    count_before = facturas.count()
    count_after = len(facturas_agrupadas)
    print(f"\nConteo de registros:")
    print(f"Antes de agrupar: {count_before}")
    print(f"Después de agrupar: {count_after}\n")

    # Obtener las líneas usadas en la consulta
    lineas_obj = Linea.objects.filter(
        Linea__in=facturas.values_list('LineaId', flat=True).distinct()
    ).distinct()
    
    return facturas_agrupadas, lineas_obj, form.cleaned_data.get('Mes') if form and form.is_valid() else None


def informe_facturacion_clientes(request):
    form = FacturacionClientesFilterForm(request.GET or None)
    
    meses_completos = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    
    facturas, lineas_filtradas, meses_filtrados = filtrar_datos(form)
    
    # Verificar datos crudos
    print("\nPrimeros 5 registros crudos:")
    for i, item in enumerate(facturas[:5]):
        print(f"{i+1}. {item}")
    
    # Filtrar meses si es necesario
    meses = [par for par in meses_completos if not meses_filtrados or str(par[0]) in meses_filtrados]
    # Estructuras de datos
    datos = {}
    totales_por_ceco = defaultdict(lambda: {'total_valor': 0})
    totales_por_linea = defaultdict(lambda: {'total_valor': 0})
    totales_por_modulo = defaultdict(lambda: {'total_valor': 0})
    totales_por_mes = defaultdict(lambda: {'total_valor': 0})
    totales_por_ceco_linea = defaultdict(lambda: defaultdict(lambda: {'total_valor': 0}))
    totales_por_ceco_linea_modulo = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'total_valor': 0})))
    
    total_global = {'total_valor': 0}

    # Contadores para depuración
    registros_procesados = 0
    registros_filtrados_por_mes = 0

    for item in facturas:
        registros_procesados += 1
        ceco = item.get('Ceco', 'Sin Ceco')
        descripcion = item.get('Descripcion', 'Sin Descripción')
        linea = item.get('LineaId__Linea', 'Sin línea')
        modulo = item.get('ModuloId__Modulo', 'Sin módulo')
        mes = int(item['Mes']) if item['Mes'] else 0
        
        valor = item['total_valor'] or 0

        # Solo procesar si el mes está en los meses filtrados
        if meses_filtrados and str(mes) not in meses_filtrados:
            registros_filtrados_por_mes += 1
            continue

        # Estructura principal de datos
        if ceco not in datos:
            datos[ceco] = {}
        if descripcion not in datos[ceco]:
            datos[ceco][descripcion] = {}
        if linea not in datos[ceco][descripcion]:
            datos[ceco][descripcion][linea] = {}
        if modulo not in datos[ceco][descripcion][linea]:
            datos[ceco][descripcion][linea][modulo] = {}
        
        datos[ceco][descripcion][linea][modulo][mes] = {
            'total_valor': valor
        }

        # Actualizar totales
        def update_totales(totales_dict, valor, *keys):
            for key in keys[:-1]:
                if key not in totales_dict:
                    if len(keys) == 1:  # Es el último nivel
                        totales_dict[key] = {'total_valor': 0}
                    else:
                        totales_dict[key] = defaultdict(lambda: {'total_valor': 0})
                totales_dict = totales_dict[key]
            
            key = keys[-1]
            if key not in totales_dict:
                totales_dict[key] = {'total_valor': 0}
            
            totales_dict[key]['total_valor'] += valor

        # Actualizar todos los totales
        update_totales(totales_por_ceco, valor, ceco)
        update_totales(totales_por_linea, valor, linea)
        update_totales(totales_por_modulo, valor, modulo)
        update_totales(totales_por_mes, valor, mes)
        update_totales(totales_por_ceco_linea, valor, ceco, linea)
        update_totales(totales_por_ceco_linea_modulo, valor, ceco, linea, modulo)
        
        total_global['total_valor'] += valor

    # Imprimir estadísticas de procesamiento
    print(f"Registros procesados: {registros_procesados}")
    print(f"Registros filtrados por mes: {registros_filtrados_por_mes}")
    print(f"Registros incluidos en el informe: {registros_procesados - registros_filtrados_por_mes}")

    # Calcular totales de filas por ceco
    cecos_con_totales = {}
    for ceco, descripciones in datos.items():
        total_filas = 0
        for descripcion, lineas in descripciones.items():
            for linea, modulos in lineas.items():
                total_filas += len(modulos)
        cecos_con_totales[ceco] = total_filas
        print(f"Ceco {ceco}: {total_filas} filas")

    # Imprimir resumen de totales
    print(f"Total de cecos distintos: {len(cecos_con_totales)}")
    print(f"Total general (valor): {total_global['total_valor']}")

    context = {
        'form': form,
        'datos': datos,
        'lineas': lineas_filtradas,
        'meses': meses,
        'cecos_con_totales': cecos_con_totales,
        'totales_por_ceco': totales_por_ceco,
        'totales_por_linea': totales_por_linea,
        'totales_por_modulo': totales_por_modulo,
        'totales_por_mes': totales_por_mes,
        'totales_por_ceco_linea': totales_por_ceco_linea,
        'totales_por_ceco_linea_modulo': totales_por_ceco_linea_modulo,
        'total_global': total_global
    }

    return render(request, 'Informes/informes_facturacion_clientes_index.html', context)