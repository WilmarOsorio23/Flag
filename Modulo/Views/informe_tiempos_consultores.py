from django.shortcuts import render, HttpResponse
import csv
from collections import defaultdict
from django.db.models import Sum
from Modulo.forms import inforTiempoEmpleadosFilterForm
from Modulo.models import Consultores, Tiempos_Cliente, Linea, Clientes
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.cell import MergedCell
from datetime import datetime
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_informe_tiempos_consultores')

def filtrar_datos(request):
    documento = request.GET.getlist('Documento')
    anio = request.GET.getlist('Anio')
    linea = request.GET.getlist('LineaId')
    mes = request.GET.getlist('Mes')

    tiempos = Tiempos_Cliente.objects.all()

    #Filtrar por documentos que existan en la tabla consultores
    if documento:
        tiempos=tiempos.filter(Documento__in=documento)
    else:
        # Filtrar directamente por documentos válidos en la consulta principal
        tiempos = Tiempos_Cliente.objects.filter(Documento__in=Consultores.objects.values_list('Documento', flat=True))
    if anio:
        tiempos = tiempos.filter(Anio=anio)
    if mes:
        tiempos =tiempos.filter(Mes=mes)
    if linea:
        tiempos= tiempos.filter(lineaId__in=linea)
    


     # Anotar el total por mes, línea y cliente
    tiempos = tiempos.values('Mes', 'LineaId', 'Documento').annotate(total=Sum('Horas'))
    return tiempos

def Filtrar_datos(forms,tiempos):
    documento = forms.cleaned_data.get('documento')
    anio = forms.cleaned_data.get('Anio')
    mes = forms.cleaned_data.get('Mes')
    linea = forms.cleaned_data.get('LineaId')

    #aplicar filtros solo si se seleccionan

    if documento:
        tiempos = tiempos.filter(Documento__in= documento)
    if anio:
        tiempos=tiempos.filter(Anio=anio)
    if mes:
        tiempos=tiempos.filter(Mes__in=mes)
    if linea:
        tiempos= tiempos.filter(LineaId__in=linea)

    return tiempos

def tiempos_clientes_filtrado(request):
    tiempos_info = []
    show_data = False

    if request.method == 'GET':
        forms = inforTiempoEmpleadosFilterForm(request.GET)

        # Obtener todos los documentos válidos de los consultores
        documentos_validos = set(Consultores.objects.values_list('Documento', flat=True))

        # Filtrar los tiempos con documentos válidos
        tiempos = Tiempos_Cliente.objects.select_related('ClienteId', 'LineaId').filter(Documento__in=documentos_validos)

        if forms.is_valid():
            # Filtrar los datos según los criterios del formulario
            tiempos = Filtrar_datos(forms, tiempos)

            # Optimiza la consulta para cargar las relaciones necesarias
            consultores = {c.Documento: c for c in Consultores.objects.select_related('ModuloId').all()}

            # Procesar los datos para incluir información adicional
            tiempos_info = [
                {
                    'Documento': t.Documento,
                    'Nombre': consultores[t.Documento].Nombre if t.Documento in consultores else '',
                    'Empresa': consultores[t.Documento].Empresa if t.Documento in consultores else '',
                    'Anio': t.Anio,
                    'Mes': t.Mes,
                    'Linea': t.LineaId.Linea if t.LineaId else '',
                    'Cliente': t.ClienteId.Nombre_Cliente if t.ClienteId else '',
                    'Modulo': consultores[t.Documento].ModuloId.Modulo if t.Documento in consultores and consultores[t.Documento].ModuloId else '',
                    'Horas': float(t.Horas),  # Convertir Decimal a float
                }
                for t in tiempos if Consultores.objects.filter(Documento=t.Documento).exists()  # Solo incluir consultores existentes
            ]
            tiempos_info.sort(key=lambda x: x['Nombre'])
            show_data = bool(tiempos_info)

        # Almacenar tiempos_info en la sesión
        request.session['tiempos_info'] = tiempos_info

    context = {
        'form': forms,
        'tiempos_info': tiempos_info,
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados" if not tiempos_info else ""
    }

    return render(request, 'informes/informes_tiempos_consultores_index.html', context)

            
def exportar_tiempos_clientes_excel(request):
    # Verificar si `tiempos_info` está en la sesión
    tiempos_info = request.session.get('tiempos_info', [])

    if not tiempos_info:
        return HttpResponse("No hay datos para exportar.")

    # Generar el Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Tiempos Consultores"

    # Definir encabezados y su orden
    encabezados = ["Documento", "Nombre", "Empresa", "Linea", "Cliente", "Modulo", "Anio", "Mes", "Horas"]

    # Estilo para bordes
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )

    # Aplicar encabezados con estilos
    for col_num, header in enumerate(encabezados, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

    # Insertar datos en el Excel con formato adecuado
    for row_num, registro in enumerate(tiempos_info, 2):
        for col_num, key in enumerate(encabezados, 1):
            value = registro.get(key, '')
            cell = ws.cell(row=row_num, column=col_num, value=value)

            # Aplicar bordes a todas las celdas
            cell.border = thin_border

            # Alinear texto en las celdas
            if isinstance(value, str):
                cell.alignment = Alignment(horizontal="left")
            elif isinstance(value, datetime):
                cell.alignment = Alignment(horizontal="center")
                cell.number_format = "YYYY-MM-DD"  # Formato de fecha

    # Ajustar automáticamente el ancho de las columnas
    for col_num, col_name in enumerate(encabezados, 1):
        max_length = len(col_name)  # Iniciar con el tamaño del encabezado

        # Revisar todas las filas de la columna para determinar el ancho máximo
        for row_num in range(2, len(tiempos_info) + 2):
            cell_value = ws.cell(row=row_num, column=col_num).value
            if cell_value:
                max_length = max(max_length, len(str(cell_value)))
        # Ajustar el ancho con un pequeño margen extra
        ws.column_dimensions[ws.cell(row=1, column=col_num).column_letter].width = max_length + 2

    # Configurar respuesta HTTP con el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    filename = f"tiempos_consultores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)

    return response
        