from django.shortcuts import render
from collections import defaultdict
from django.http import HttpResponse
from Modulo.forms import OtrosSiFilterForm
from Modulo.models import Clientes, ContratosOtrosSi, ClientesContratos
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from datetime import datetime
from django.http import JsonResponse
from Modulo.models import Clientes

def get_cliente_id_by_nombre(request):
    nombre = request.GET.get('nombre')
    cliente = Clientes.objects.filter(Nombre_Cliente=nombre).first()
    if cliente:
        return JsonResponse({'cliente_id': cliente.ClienteId})
    return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

# Filtrar OtrosSí por cliente y fecha de inicio
def filtrar_otros_si(form, clientes, otros_si):
    clientes = clientes.order_by('Nombre_Cliente')
    nombre = form.cleaned_data.get('Nombre_Cliente')
    fecha_inicio = form.cleaned_data.get('FechaInicio')
    contrato = form.cleaned_data.get('Contrato')
    contrato_vigente = form.cleaned_data.get('ContratoVigente') 

    if nombre:
        clientes = clientes.filter(Nombre_Cliente=nombre)
    if fecha_inicio:
        otros_si = otros_si.filter(FechaInicio=fecha_inicio)
    if contrato:
        otros_si = otros_si.filter(Contrato__iexact=contrato.strip())

    if contrato_vigente in ('True', 'False'):
        # Obtener contratos de ClientesContratos que tengan ese estado
        contratos_filtrados = ClientesContratos.objects.filter(
            ContratoVigente=(contrato_vigente == 'True')
        ).values_list('Contrato', flat=True)

        # Filtrar ContratosOtrosSi por los contratos que coincidan
        otros_si = otros_si.filter(Contrato__in=contratos_filtrados)
    
    cliente_ids = otros_si.values_list('ClienteId', flat=True)
    clientes = clientes.filter(ClienteId__in=cliente_ids)

    return clientes, otros_si

# Obtener información del informe
def obtener_otros_si(clientes, otros_si):
    cliente_otros_si_info = []
    otros_si_por_cliente = defaultdict(list)

    for registro in otros_si:
        otros_si_por_cliente[registro.ClienteId_id].append(registro)

    for cliente in clientes:
        otros_cliente = otros_si_por_cliente.get(cliente.ClienteId, [])

        datos_cliente = {
            'documento': cliente.DocumentoId,
            'nombre': cliente.Nombre_Cliente,
            'otros_si': [{
                'FechaInicio': registro.FechaInicio,
                'FechaFin': registro.FechaFin,
                'NumeroOtroSi': registro.NumeroOtroSi,
                'ValorOtroSi': registro.ValorOtroSi,
                'ValorIncluyeIva': registro.ValorIncluyeIva,
                'Polizas': registro.Polizas,
                'PolizasDesc': registro.PolizasDesc,
                'FirmadoFlag': registro.FirmadoFlag,
                'FirmadoCliente': registro.FirmadoCliente,
                'Contrato': registro.Contrato,
                'moneda': registro.monedaId.Nombre if registro.monedaId else "Sin Moneda"
            } for registro in otros_cliente]
        }

        cliente_otros_si_info.append(datos_cliente)

    return cliente_otros_si_info

# Vista HTML
def informe_otros_si(request):
    cliente_otros_si_info = []
    show_data = False

    if request.method == 'GET':
        form = OtrosSiFilterForm(request.GET)

        if form.is_valid():
            clientes = Clientes.objects.only('Nombre_Cliente', 'ClienteId').filter(Activo=True)
            otros_si = ContratosOtrosSi.objects.select_related('ClienteId', 'monedaId').all()

            clientes, otros_si = filtrar_otros_si(form, clientes, otros_si)
            cliente_otros_si_info = obtener_otros_si(clientes, otros_si)
            show_data = bool(cliente_otros_si_info)
        else:
            print("Errores del formulario:", form.errors)
    else:
        form = OtrosSiFilterForm()

    context = {
        'form': form,
        'cliente_otros_si_info': cliente_otros_si_info,
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not cliente_otros_si_info else "",
    }

    return render(request, 'informes/informes_otros_si_index.html', context)

# Exportar a Excel
def exportar_otros_si_excel(request):
    cliente_otros_si_info = []

    if request.method == 'GET':
        form = OtrosSiFilterForm(request.GET)

        if form.is_valid():
            clientes = Clientes.objects.only('Nombre_Cliente', 'ClienteId').filter(Activo=True)
            otros_si = ContratosOtrosSi.objects.select_related('ClienteId', 'monedaId').all()

            clientes, otros_si = filtrar_otros_si(form, clientes, otros_si)
            cliente_otros_si_info = obtener_otros_si(clientes, otros_si)

            if not cliente_otros_si_info:
                return HttpResponse("No se encontraron resultados para los filtros aplicados.")
        else:
            print("Errores del formulario:", form.errors)
            return HttpResponse("No se encontraron resultados para los filtros aplicados.")

        data = []
        for cliente in cliente_otros_si_info:
            for registro in cliente['otros_si']:
                data.append([
                    cliente['documento'],
                    cliente['nombre'],
                    registro['FechaInicio'],
                    registro['FechaFin'],
                    registro['NumeroOtroSi'],
                    registro['Contrato'],
                    registro['ValorOtroSi'],
                    'SI' if registro['ValorIncluyeIva'] else 'NO',
                    'SI' if registro['Polizas'] else 'NO',
                    registro['PolizasDesc'],
                    'SI' if registro['FirmadoFlag'] else 'NO',
                    'SI' if registro['FirmadoCliente'] else 'NO',
                    registro['moneda'],
                ])

        # Crear Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Informe Otros Sí"

        encabezados = [
            'Documento Cliente',
            'Nombre Cliente',
            'Fecha Inicio',
            'Fecha Fin',
            'Número OtroSí',
            'Contrato',
            'Valor OtroSí',
            'Incluye IVA',
            'Polizas',
            'Descripción Polizas',
            'Firmado (Interno)',
            'Firmado Cliente',
            'Moneda',
        ]

        for col_num, header in enumerate(encabezados, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

        for row_num, row in enumerate(data, 2):
            for col_num, value in enumerate(row, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                cell.alignment = Alignment(horizontal='center')

        for column in ws.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column[0].column_letter].width = adjusted_width

        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                             top=Side(style='thin'), bottom=Side(style='thin'))

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in row:
                cell.border = thin_border

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"otros_si_reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)

        return response
