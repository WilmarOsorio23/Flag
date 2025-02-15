from django.shortcuts import render
from django.http import HttpResponse
from Modulo.forms import ConsultorFilterForm
from Modulo.models import Consultores
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from datetime import datetime

#Función para filtrar Consultores
#Filtros: Nombre Consultor, Linea, Modulo, Certificación, Perfil
def filtrar_consultores(form, consultores):
    consultores = consultores.order_by('Nombre')
    nombre = form.cleaned_data.get('Nombre')
    linea = form.cleaned_data.get('LineaId')
    modulo = form.cleaned_data.get('ModuloId')
    certificacion = form.cleaned_data.get('Certificacion')
    perfil = form.cleaned_data.get('PerfilId')
    estado = form.cleaned_data.get('Estado')

    if nombre:
        consultores = consultores.filter(Nombre=nombre)
    if linea:
        consultores = consultores.filter(LineaId=linea)
    if modulo:
        consultores = consultores.filter(ModuloId=modulo)
    if certificacion:
        consultores = consultores.filter(Certificado=bool(int(certificacion)))
    if perfil:
        consultores = consultores.filter(PerfilId=perfil)
    if estado:
        consultores = consultores.filter(Estado=bool(int(estado)))

    return consultores

#Función para obtener información de los consultores
def obtener_consultores(consultores):
    consultor_info = []

    for consultor in consultores:
        datos_consultor = {
            'documento': consultor.Documento,
            'tipo_documento': consultor.TipoDocumentoID.Nombre,
            'nombre': consultor.Nombre,
            'empresa': consultor.Empresa,
            'profesion': consultor.Profesion,
            'linea': consultor.LineaId.Linea,
            'modulo': consultor.ModuloId.Modulo,
            'perfil': consultor.PerfilId.Perfil,
            'estado': 'Activo' if consultor.Estado else 'Inactivo',
            'fecha_ingreso': consultor.Fecha_Ingreso.strftime('%Y-%m-%d') if consultor.Fecha_Ingreso else '',
            'fecha_retiro': consultor.Fecha_Retiro.strftime('%Y-%m-%d') if consultor.Fecha_Retiro else '',
            'direccion': consultor.Direccion,
            'telefono': consultor.Telefono,
            'fecha_operacion': consultor.Fecha_Operacion.strftime('%Y-%m-%d %H:%M:%S') if consultor.Fecha_Operacion else '',
            'certificado':  'SI' if consultor.Certificado else 'NO',
            'certificaciones': consultor.Certificaciones,
        }

        consultor_info.append(datos_consultor)
    return consultor_info

def consultores_filtrado(request):
    consultor_info = []
    show_data = False  

    if request.method == 'GET':
        form = ConsultorFilterForm(request.GET)

        if form.is_valid():
            # Inicializar consultores
            consultores = Consultores.objects.all()

            # Relizar el filtro de los consultores
            consultores = filtrar_consultores(form, consultores)

            #Obtener informacion de consultores 
            consultor_info = obtener_consultores(consultores)
            show_data = bool(consultor_info)  # Mostrar datos si hay resultados
        
    else: 
        form = ConsultorFilterForm()

    context = {
        'form': form,
        'consultor_info': consultor_info,      
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not consultor_info else ""
    }

    return render(request, 'informes/informes_consultores_index.html', context)


def exportar_consultores_excel(request):
    consultor_info = []
    
    if request.method == 'GET':
        form = ConsultorFilterForm(request.GET)

        if form.is_valid():
            # Inicializar consultores
            consultores = Consultores.objects.all()

            # Obtener información de los empleados filtrada
            consultores = filtrar_consultores(form, consultores)
            
            # Obtener información de los consultores
            consultor_info = obtener_consultores(consultores)
                        
            if not consultor_info:
                return HttpResponse("No se encontraron datos para exportar.")
                
        else: 
                print("Errores del formulario:", form.errors)
                return HttpResponse("Filtros no válidos.", status=400)

        #Preparar datos para excel 
        data = []
        for consultor in consultor_info:
            fila = {
                'Documento': consultor['documento'],
                'Tipo Documento': consultor['tipo_documento'],
                'Nombre': consultor['nombre'],
                'Empresa': consultor['empresa'],
                'Profesión': consultor['profesion'],
                'Línea': consultor['linea'],
                'Módulo': consultor['modulo'],
                'Perfil': consultor['perfil'],
                'Estado': consultor['estado'],
                'Fecha Ingreso': consultor['fecha_ingreso'],
                'Fecha Retiro': consultor['fecha_retiro'],
                'Dirección': consultor['direccion'],
                'Teléfono': consultor['telefono'],
                'Fecha Operación': consultor['fecha_operacion'],
                'Certificado': consultor['certificado'],
                'Certificaciones': consultor['certificaciones'],
            }
            data.append(fila)

        # Crear un libro de trabajo y una hoja
        wb = Workbook()
        ws = wb.active
        ws.title = "Informe de Consultores"

        # Agregar encabezados
        for col in data[0].keys():
            cell = ws.cell(row=1, column=list(data[0].keys()).index(col) + 1, value=col)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

        # Agregar datos del DataFrame a la hoja
        for r_idx, row in enumerate(data, 2):
            for c_idx, value in enumerate(row.values(), 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                cell.alignment = Alignment(horizontal='center')  # Centrar datos

        # Ajustar el ancho de las columnas
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

        # Crear respuesta de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"consultores_reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # Guardar el libro de trabajo en la respuesta  
        wb.save(response)

        return response
    return HttpResponse("Método no permitido", status=405)
        