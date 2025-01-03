from django.shortcuts import render
from datetime import date, datetime
from collections import defaultdict
from Modulo.forms import EmpleadoFilterForm
from Modulo.models import Empleado
from django.http import HttpResponse
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

# Función para filtrar empleados
def filtrar_empleados(form, empleados):
    empleados = empleados.order_by('Documento')  # Ordenar por Documento

    documento = form.cleaned_data.get('Documento')
    linea = form.cleaned_data.get('Linea')
    cargo = form.cleaned_data.get('Cargo')
    certificados = form.cleaned_data.get('Certificados')
    perfil = form.cleaned_data.get('Perfil')

    if documento:
        empleados = empleados.filter(Documento=documento)
    if linea:
        empleados = empleados.filter(LineaId=linea)
    if cargo:
        empleados = empleados.filter(CargoId=cargo)
    if certificados:
        empleados = empleados.filter(CertificadoSAP__icontains=certificados)
    if perfil:
        empleados = empleados.filter(PerfilId=perfil)

    return empleados

# Función para obtener la información del informe
def obtener_informe_empleados(empleados):
    informe = []

    for empleado in empleados:
        informe.append({
            'tipo_documento': empleado.TipoDocumento,
            'documento': empleado.Documento,
            'nombre': empleado.Nombre,
            'fecha_nacimiento': empleado.FechaNacimiento,
            'fecha_ingreso': empleado.FechaIngreso,
            'fecha_operacion': empleado.FechaOperacion,
            'modulo': empleado.ModuloId,
            'perfil': empleado.PerfilId,
            'linea': empleado.LineaId,
            'titulo_profesional': empleado.TituloProfesional,
            'fecha_grado': empleado.FechaGrado,
            'universidad': empleado.Universidad,
            'profesion_realizada': empleado.ProfesionRealizada,
            'titulo_profesional_actual': empleado.TituloProfesionalActual,
            'universidad_actual': empleado.UniversidadActual,
            'academia_sap': empleado.AcademiaSAP,
            'certificado_sap': empleado.CertificadoSAP,
            'otras_certificaciones': empleado.OtrasCertificaciones,
            'postgrados': empleado.Postgrados,
        })

    return informe

# Vista del informe de empleados
def informe_empleados(request):
    empleados_info = []
    show_data = False

    if request.method == 'GET':
        form = EmpleadoFilterForm(request.GET)

        if form.is_valid():
            empleados = Empleado.objects.all()

            # Aplicar filtros
            empleados = filtrar_empleados(form, empleados)

            # Obtener la información del informe
            empleados_info = obtener_informe_empleados(empleados)
            show_data = bool(empleados_info)

    else:
        form = EmpleadoFilterForm()

    context = {
        'form': form,
        'empleados_info': empleados_info,
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not empleados_info else ""
    }

    return render(request, 'informes/informes_empleado_index.html', context)

# Exportar informe de empleados a Excel
def exportar_empleados_excel(request):
    empleados_info = []

    if request.method == 'GET':
        form = EmpleadoFilterForm(request.GET)

        if form.is_valid():
            empleados = Empleado.objects.all()

            # Aplicar filtros
            empleados = filtrar_empleados(form, empleados)

            # Obtener la información del informe
            empleados_info = obtener_informe_empleados(empleados)

        if not empleados_info:
            return HttpResponse("No se encontraron datos para exportar.", status=404)

        if not form.is_valid():
            return HttpResponse("Filtros no válidos. Por favor, revisa los criterios ingresados.", status=400)

    # Crear libro de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Informe de Empleados"

    # Agregar encabezados
    encabezados = list(empleados_info[0].keys())
    for col_idx, encabezado in enumerate(encabezados, start=1):
        cell = ws.cell(row=1, column=col_idx, value=encabezado)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    # Agregar datos
    for row_idx, empleado in enumerate(empleados_info, start=2):
        for col_idx, (key, value) in enumerate(empleado.items(), start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = Alignment(horizontal='center')

    # Ajustar ancho de columnas
    for column_cells in ws.columns:
        max_length = max((len(str(cell.value)) if cell.value else 0) for cell in column_cells)
        adjusted_width = max_length + 2
        ws.column_dimensions[column_cells[0].column_letter].width = adjusted_width

    # Aplicar bordes a las celdas
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            cell.border = thin_border

    # Crear respuesta de Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"informe_empleados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)

    return response
