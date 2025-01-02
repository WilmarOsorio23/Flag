# Informe de Certificación de Empleados
from django.shortcuts import render
from openpyxl import Workbook
from Modulo.Views import Certificacion
from Modulo.forms import EmpleadoFilterForm
from Modulo.models import Detalle_Certificacion, Empleado


def empleado_filtrado(request):
    empleados = Empleado.objects.all()
    certificaciones = Certificacion.objects.all()
    detalles_certificacion = Detalle_Certificacion.objects.all()

    empleado_info = None
    show_data = False  # Solo mostramos resultados si hay filtros aplicados

    # Verifica si se han enviado parámetros de búsqueda (GET)
    if request.method == 'GET':
        form = EmpleadoFilterForm(request.GET)

        if form.is_valid():
            # Obtiene los valores del formulario
            nombre = form.cleaned_data.get('Nombre')
            certificacion = form.cleaned_data.get('Certificacion')
            linea = form.cleaned_data.get('LineaId')
            modulo_id = form.cleaned_data.get('ModuloId')
            fecha_certificacion = form.cleaned_data.get('Fecha_Certificacion')

            # Filtrar empleados con los valores del formulario
            if nombre:
                empleados = empleados.filter(Nombre__icontains=nombre)
            if linea:
                empleados = empleados.filter(LineaId=linea)
            if modulo_id:
                empleados = empleados.filter(ModuloId=modulo_id)

            # Filtrar detalles de certificación por los empleados encontrados
            if empleados.exists():
                detalles_certificacion = detalles_certificacion.filter(DocumentoId__in=empleados.values_list('Documento', flat=True))

            # Filtrar por certificación
            if certificacion:
                detalles_certificacion = detalles_certificacion.filter(CertificacionId=certificacion)

            # Filtrar por fecha de certificación
            if fecha_certificacion:
                detalles_certificacion = detalles_certificacion.filter(Fecha_Certificacion=fecha_certificacion)

            # Crear la estructura de empleado_info solo si hay detalles de certificación encontrados
            if detalles_certificacion.exists():
                empleado_info = []
                for empleado in empleados:
                    certs = detalles_certificacion.filter(DocumentoId=empleado.Documento)
                    if certs.exists():
                        empleado_info.append({
                            'empleado': empleado,
                            'certificaciones': certs
                        })

            show_data = True
    else:
        form = EmpleadoFilterForm()

    context = {
        'form': form,
        'empleados': empleados,
        'certificaciones': certificaciones,
        'detalles_certificacion': detalles_certificacion,
        'empleado_info': empleado_info,
        'show_data': show_data,
    }

    return render(request, 'informes/informes_certificacion_index.html', context)


# Funcionalidad para descargar los resultados Certificado en Excel
def exportar_excel(request):
    empleados = Empleado.objects.all().select_related('LineaId', 'ModuloId', 'PerfilId').prefetch_related(
        Prefetch('detallecertificacion_set', queryset=Detalle_Certificacion.objects.select_related('CertificacionId')) # type: ignore
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Empleados con Certificaciones"
    ws.append([
         'Nombre', 'Línea', 'Módulo', 'Documento', 'Cargo', 'Perfil', 'Certificación', 'Fecha Certificación'
    ])

    for empleado in empleados:
        for detalle in empleado.detalle_certificacion.all():
            ws.append([
                empleado.Documento,
                empleado.Nombre,
                empleado.LineaId.Nombre if empleado.LineaId else '',
                empleado.ModuloId.Nombre if empleado.ModuloId else '',
                empleado.Documento,
                empleado.Cargo,
                empleado.PerfilId.Nombre if empleado.PerfilId else '',
            ])

    response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') # type: ignore
    response['Content-Disposition'] = 'attachment; filename=empleados_certificaciones.xlsx'

