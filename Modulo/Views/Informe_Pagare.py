import logging
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from Modulo.forms import EmpleadoConPagareFilterForm
from Modulo.models import Empleado, Pagare
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

def calcular_meses_condonados(fecha_inicio):
    if not fecha_inicio or not isinstance(fecha_inicio, date):
        return 0
    
    hoy = date.today()
    if fecha_inicio > hoy:
        return 0
    
    diferencia = relativedelta(hoy, fecha_inicio)
    meses = diferencia.years * 12 + diferencia.months
    
    if hoy.day < fecha_inicio.day:
        meses -= 1
    
    return max(0, meses)

def filtrar_pagares(form, pagarés):
    empleados = form.cleaned_data.get('empleados_con_pagare')
    anio = form.cleaned_data.get('Anio')
    lineas = form.cleaned_data.get('LineaId')
    tipos = form.cleaned_data.get('tipo_pagare')

    if empleados:
        pagarés = pagarés.filter(Documento__in=empleados.values_list('Documento', flat=True))
    if anio:
        pagarés = pagarés.filter(Fecha_Creacion_Pagare__year=anio)
    if lineas:
        pagarés = pagarés.filter(Documento__in=Empleado.objects.filter(LineaId__in=lineas).values_list('Documento', flat=True))
    if tipos:
        pagarés = pagarés.filter(Tipo_Pagare__in=tipos)

    return pagarés

def informe_pagares(request):
    pagarés_info = []
    show_data = False
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    form = EmpleadoConPagareFilterForm(request.GET or None)
    pagarés = Pagare.objects.select_related('Tipo_Pagare').all()

    print(f"Datos recibidos en el formulario: {request.GET}")

    if form.is_valid():
        pagarés = filtrar_pagares(form, pagarés)
        documentos = pagarés.values_list('Documento', flat=True).distinct()
        empleados = Empleado.objects.filter(Documento__in=documentos).select_related('LineaId', 'CargoId')
        empleados_dict = {emp.Documento: emp for emp in empleados}

        print(f"Pagarés recuperados: {pagarés}")
        print(f"Empleados recuperados: {empleados}")

        for pagare in pagarés:
            empleado = empleados_dict.get(pagare.Documento)

            if empleado:
                fecha_inicio_condonacion = pagare.Fecha_inicio_Condonacion
                meses_condonados = calcular_meses_condonados(fecha_inicio_condonacion)

                valor_condonado = 0
                if pagare.Meses_de_condonacion and pagare.Meses_de_condonacion > 0:
                    meses_efectivos = min(meses_condonados, pagare.Meses_de_condonacion)
                    valor_condonado = (float(pagare.Valor_Pagare) / pagare.Meses_de_condonacion) * meses_efectivos

                deuda_pagare = float(pagare.Valor_Pagare) - valor_condonado

                meses_por_condonar = 0
                if pagare.Meses_de_condonacion:
                    meses_por_condonar = max(0, pagare.Meses_de_condonacion - meses_condonados)

                porcentaje_ejecucion = 0.0
                if pagare.Meses_de_condonacion and pagare.Meses_de_condonacion > 0:
                    porcentaje_ejecucion = (meses_condonados / pagare.Meses_de_condonacion) * 100

                registro = {
                    'Documento': empleado.Documento,
                    'Nombre': empleado.Nombre,
                    'Linea': empleado.LineaId.Linea if empleado.LineaId else 'N/A',
                    'Cargo': empleado.CargoId.Cargo if empleado.CargoId else 'N/A',
                    'FechaIngreso': empleado.FechaIngreso.strftime("%Y-%m-%d") if empleado.FechaIngreso else "",
                    'FechaOperacion': empleado.FechaOperacion.strftime("%Y-%m-%d") if empleado.FechaOperacion else "",
                    'ConsecutivoPagare': pagare.Pagare_Id,
                    'FechaPagare': pagare.Fecha_Creacion_Pagare.strftime("%Y-%m-%d") if pagare.Fecha_Creacion_Pagare else "",
                    'FechaInicioCondonacion': fecha_inicio_condonacion.strftime("%Y-%m-%d") if fecha_inicio_condonacion else "",
                    'FechaFinCondonacion': pagare.Fecha_fin_Condonacion.strftime("%Y-%m-%d") if pagare.Fecha_fin_Condonacion else "",
                    'ValorPagare': float(pagare.Valor_Pagare),
                    'MesesCondonacion': pagare.Meses_de_condonacion if pagare.Meses_de_condonacion else 0,
                    'PorcentajeEjecucion': round(porcentaje_ejecucion, 2),
                    'FechaRetiro': empleado.FechaRetiro.strftime("%Y-%m-%d") if empleado.FechaRetiro else "",
                    'ValorCondonado': valor_condonado,
                    'DeudaPagare': deuda_pagare,
                    'MesesCondonados': meses_condonados,
                    'MesesPorCondonar': meses_por_condonar,
                    'pagare_id': pagare.Pagare_Id
                }
                pagarés_info.append(registro)

        print(f"Datos procesados para la tabla: {pagarés_info}")

        show_data = bool(pagarés_info)
        request.session['pagares_info'] = pagarés_info  # Guardar los datos en la sesión
    else:
        print(f"Errores en el formulario: {form.errors}")

    context = {
        'form': form,
        'pagares_info': pagarés_info,
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados" if not pagarés_info else "",
        'fecha_actual': fecha_actual
    }   

    return render(request, 'Pagare/Informe_Pagare.html', context)

def exportar_pagares_excel(request):
    # Obtener datos de la sesión
    pagarés_info = request.session.get('pagares_info', [])
    logger.debug(f"Pagarés en la sesión: {pagarés_info}")
    logger.debug(f"Datos recibidos: {request.GET}")

    if not pagarés_info:
        return HttpResponse("No hay datos para exportar.")
    
    # Determinar qué registros exportar
    export_all = request.GET.get('export_all', '0') == '1'
    selected_ids_str = request.GET.get('selected_ids', '')
    selected_ids = selected_ids_str.split(',') if selected_ids_str else []
    fecha_informe = request.GET.get('fecha_informe', datetime.now().strftime("%Y-%m-%d"))
    
    if export_all:
        # Exportar todos los registros filtrados
        pass  # Ya tenemos todos los datos en pagarés_info
    elif selected_ids:
        # Exportar solo los seleccionados
        pagarés_info = [p for p in pagarés_info if str(p.get('ConsecutivoPagare', '')) in selected_ids]
    else:
        # Exportar todo si no hay selección
        pass  # Ya tenemos todos los datos en pagarés_info

    if not pagarés_info:
        return HttpResponse("No hay datos para exportar.")

    wb = Workbook()
    ws = wb.active
    ws.title = "Informe de Pagarés"

    # Fecha del informe
    ws.cell(row=1, column=1, value="Fecha del informe:")
    ws.cell(row=1, column=1).font = Font(bold=True)
    ws.cell(row=1, column=2, value=fecha_informe)
    
    # Encabezados de la tabla resumen
    columnas = [
        "Documento", "Nombre", "Línea", "Cargo", 
        "Fecha Ingreso", "Fecha Inicio Operación", "Consecutivo Pagare", 
        "Fecha Pagare", "Fecha Inicio Condonación", "Fecha Fin Condonación", 
        "Valor del Pagaré", "Valor Condonado", "Deuda Pagare", 
        "Meses Condonación", "Meses Condonados", "Meses por Condonar", 
        "%Ejecución", "Fecha Retiro"
    ]

    # Escribir encabezados (fila 3)
    for col_num, header in enumerate(columnas, 1):
        cell = ws.cell(row=3, column=col_num, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Datos resumen (a partir de fila 4)
    row_num = 4
    for registro in pagarés_info:
        ws.cell(row=row_num, column=1, value=registro.get('Documento', ''))
        ws.cell(row=row_num, column=2, value=registro.get('Nombre', ''))
        ws.cell(row=row_num, column=3, value=registro.get('Linea', ''))
        ws.cell(row=row_num, column=4, value=registro.get('Cargo', ''))
        ws.cell(row=row_num, column=5, value=registro.get('FechaIngreso', ''))
        ws.cell(row=row_num, column=6, value=registro.get('FechaOperacion', ''))
        ws.cell(row=row_num, column=7, value=registro.get('ConsecutivoPagare', ''))
        ws.cell(row=row_num, column=8, value=registro.get('FechaPagare', ''))
        ws.cell(row=row_num, column=9, value=registro.get('FechaInicioCondonacion', ''))
        ws.cell(row=row_num, column=10, value=registro.get('FechaFinCondonacion', ''))
        ws.cell(row=row_num, column=11, value=registro.get('ValorPagare', 0))
        ws.cell(row=row_num, column=12, value=registro.get('ValorCondonado', 0))
        ws.cell(row=row_num, column=13, value=registro.get('DeudaPagare', 0))
        ws.cell(row=row_num, column=14, value=registro.get('MesesCondonacion', 0))
        ws.cell(row=row_num, column=15, value=registro.get('MesesCondonados', 0))
        ws.cell(row=row_num, column=16, value=registro.get('MesesPorCondonar', 0))
        ws.cell(row=row_num, column=17, value=registro.get('PorcentajeEjecucion', 0))
        ws.cell(row=row_num, column=18, value=registro.get('FechaRetiro', ''))
        row_num += 1

    # Ajustar anchos de columna para resumen
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Ahora, en la misma hoja, agregamos el detalle de cuotas
    # Dejamos 2 filas de separación
    row_num += 2

    # Título para el detalle de cuotas
    ws.merge_cells(start_row=row_num, start_column=1, end_row=row_num, end_column=6)
    title_cell = ws.cell(row=row_num, column=1, value="Detalle de Cuotas")
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal='center')
    row_num += 1

    # Encabezados para detalle
    encabezados_detalle = ["Documento", "Nombre", "No. Cuota", "Fecha Cuota", "Valor cuota", "Estado"]
    # Escribir encabezados
    for col_num, header in enumerate(encabezados_detalle, 1):
        cell = ws.cell(row=row_num, column=col_num, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
    row_num += 1

    # Generar datos detalle de cuotas
    for registro in pagarés_info:
    # Obtener datos del pagaré
        valor_pagare = float(registro.get('ValorPagare', 0))
        meses_condonacion = int(registro.get('MesesCondonacion', 0))
        fecha_inicio_condonacion_str = registro.get('FechaInicioCondonacion')
        documento = registro.get('Documento', '')
        nombre = registro.get('Nombre', '')

        # Convertir fecha_inicio_condonacion a un objeto date si es una cadena
        fecha_inicio_condonacion = None
        if fecha_inicio_condonacion_str:
            try:
                fecha_inicio_condonacion = datetime.strptime(fecha_inicio_condonacion_str, "%Y-%m-%d").date()
            except ValueError:
                fecha_inicio_condonacion = None

        # Generar cuotas incluso si la fecha de inicio de condonación está vacía
        if valor_pagare > 0 and meses_condonacion > 0:
            valor_cuota = valor_pagare / meses_condonacion

            for i in range(1, meses_condonacion + 1):
                fecha_cuota_str = ""
                estado = ""

                if fecha_inicio_condonacion:
                    # Calcular fecha de la cuota
                    fecha_cuota = fecha_inicio_condonacion + relativedelta(months=(i - 1))
                    fecha_cuota_str = fecha_cuota.strftime("%d/%m/%Y")

                    # Determinar estado de la cuota
                    estado = "Pago" if fecha_cuota < date.today() else "Pendiente"

                # Escribir fila en Excel
                ws.cell(row=row_num, column=1, value=documento)
                ws.cell(row=row_num, column=2, value=nombre)
                ws.cell(row=row_num, column=3, value=i)
                ws.cell(row=row_num, column=4, value=fecha_cuota_str)
                ws.cell(row=row_num, column=5, value=valor_cuota)
                ws.cell(row=row_num, column=6, value=estado)
                row_num += 1
        else:
            # Si no hay datos válidos, generar filas vacías
            for i in range(1, meses_condonacion + 1):
                ws.cell(row=row_num, column=1, value=documento)
                ws.cell(row=row_num, column=2, value=nombre)
                ws.cell(row=row_num, column=3, value=i)
                ws.cell(row=row_num, column=4, value="")  # Fecha vacía
                ws.cell(row=row_num, column=5, value=valor_pagare / meses_condonacion if meses_condonacion > 0 else 0)
                ws.cell(row=row_num, column=6, value="")  # Estado vacío
                row_num += 1

    # Ajustar anchos de columna para la sección de detalle
    for col_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
        max_length = 0
        col_idx = ord(col_letter) - 64  # Convertir letra a índice numérico (A=1, B=2, etc)
        for row in range(1, row_num):
            cell_value = ws.cell(row=row, column=col_idx).value
            if cell_value:
                try:
                    cell_length = len(str(cell_value))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass
        adjusted_width = max_length + 2
        ws.column_dimensions[col_letter].width = adjusted_width

    # Guardar y devolver el Excel
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename="informe_pagares_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    wb.save(response)
    return response