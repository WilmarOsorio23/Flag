from django.shortcuts import render, HttpResponse
from collections import defaultdict
from django.db.models import Sum
from Modulo.forms import InformeFacturacionForm
from Modulo.models import FacturacionClientes, Linea, Clientes
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from datetime import datetime

# Función para filtrar datos
def filtrar_datos(form):
    anio = form.cleaned_data.get('Anio')
    lineas = form.cleaned_data.get('LineaId')
    clientes = form.cleaned_data.get('ClienteId')

    facturas = FacturacionClientes.objects.all()

    # Aplicar filtros solo si se seleccionan
    if anio:
        facturas = facturas.filter(Anio=anio)
    if lineas:
        facturas = facturas.filter(LineaId__in=lineas)
    else:
        lineas = Linea.objects.all()  # Traer todas las líneas si no se selecciona ninguna
    if clientes:
        facturas = facturas.filter(ClienteId__in=clientes)
    else:
        clientes = Clientes.objects.all()  # Traer todos los clientes si no se selecciona ninguno

    facturas = facturas.values('Mes', 'LineaId', 'ClienteId').annotate(total=Sum('Valor'))
    return facturas, lineas, clientes

# Función para organizar los datos
def organizar_datos(facturas, lineas, clientes):
    meses = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]

    totales = {
        'por_linea': defaultdict(lambda: defaultdict(float)),
        'general': defaultdict(float),
        'clientes': defaultdict(lambda: defaultdict(lambda: defaultdict(float))),
        'footer': {
            'por_linea': defaultdict(float),
            'general': 0,
            'clientes': defaultdict(lambda: defaultdict(float))
        }
    }

    for f in facturas:
        mes = f['Mes']
        linea = f['LineaId']
        cliente = f['ClienteId']
        total = f['total'] or 0

        totales['por_linea'][mes][linea] += total
        totales['footer']['por_linea'][linea] += total

        totales['general'][mes] += total
        totales['footer']['general'] += total

        totales['clientes'][cliente][mes][linea] += total
        totales['footer']['clientes'][cliente][linea] += total

    rows = []
    for mes_num, mes_nombre in meses:
        row = {
            'mes': mes_nombre,
            'totales_linea': [totales['por_linea'][mes_num].get(linea.LineaId, 0) for linea in lineas],
            'total_general': totales['general'].get(mes_num, 0),
            'clientes': []
        }

        for cliente in clientes:
            cliente_data = {
                'id': cliente.ClienteId,
                'totales': [totales['clientes'][cliente.ClienteId][mes_num].get(linea.LineaId, 0) for linea in lineas]
            }
            row['clientes'].append(cliente_data)

        rows.append(row)

    footer = {
        'totales_linea': [totales['footer']['por_linea'][linea.LineaId] for linea in lineas],
        'total_general': totales['footer']['general'],
        'clientes': []
    }

    for cliente in clientes:
        cliente_data = {
            'id': cliente.ClienteId,
            'totales': [totales['footer']['clientes'][cliente.ClienteId][linea.LineaId] for linea in lineas]
        }
        footer['clientes'].append(cliente_data)

    return rows, footer, lineas, clientes, meses

# Función para generar el reporte en el frontend
def informes_facturacion_index(request):
    form = InformeFacturacionForm(request.GET or None)
    mensaje = None
    rows = None
    footer = None
    lineas = None
    clientes = None
    meses = None

    if form.is_valid():
        facturas, lineas, clientes = filtrar_datos(form)
        if facturas.exists():
            rows, footer, lineas, clientes, meses = organizar_datos(facturas, lineas, clientes)
        else:
            mensaje = "No se encontraron datos con los filtros seleccionados."
    else:
        mensaje = "Por favor, corrige los errores en el formulario."

    context = {
        'form': form,
        'rows': rows,
        'footer': footer,
        'lineas': lineas,
        'clientes': clientes,
        'meses': meses,
        'mensaje': mensaje
    }
    return render(request, 'Informes/informes_facturacion_index.html', context)

# Función para descargar el reporte en Excel
def descargar_reporte_excel(request):
    form = InformeFacturacionForm(request.GET or None)

    if form.is_valid():
        facturas, lineas, clientes = filtrar_datos(form)
        if facturas.exists():
            rows, footer, lineas, clientes, meses = organizar_datos(facturas, lineas, clientes)

            # Preparar datos para Excel
            data = []
            for row in rows:
                for cliente in row['clientes']:
                    data.append([
                        row['mes'],
                        *row['totales_linea'],
                        row['total_general'],
                        *cliente['totales']
                    ])

            # Crear libro de Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "Informe de Facturación"

            # Encabezados
            encabezados = ["Mes", *[linea.Linea for linea in lineas], "Total General", *[f"{cliente.Nombre_Cliente} - {linea.Linea}" for cliente in clientes for linea in lineas]]
            for col_num, header in enumerate(encabezados, 1):
                cell = ws.cell(row=1, column=col_num, value=header)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')

            # Datos
            for row_num, row in enumerate(data, 2):
                for col_num, value in enumerate(row, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=value)
                    cell.alignment = Alignment(horizontal='center')

            # Ajustar columnas
            for column in ws.columns:
                max_length = max(len(str(cell.value)) for cell in column)
                ws.column_dimensions[column[0].column_letter].width = max_length + 2

            # Bordes
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                             top=Side(style='thin'), bottom=Side(style='thin'))
            for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
                for cell in row:
                    cell.border = thin_border

            # Respuesta
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = f"informe_facturacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            wb.save(response)
            return response
        else:
            return HttpResponse("No se encontraron datos para exportar.")
    else:
        return HttpResponse("Formulario no válido.")