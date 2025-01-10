from django.shortcuts import render
from datetime import date, datetime
from collections import defaultdict
from Modulo.forms import EmpleadoFilterForm
from Modulo.models import Empleado, Nomina
from django.http import HttpResponse
from django.db.models import Q
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

# Función para filtrar empleados y nóminas
def filtrar_empleados(form, empleados):
    """
    Aplica filtros a un QuerySet de empleados basado en los datos del formulario.

    :param form: Instancia de EmpleadoFilterForm con datos validados.
    :param empleados: QuerySet de empleados.
    :return: QuerySet filtrado.
    """
    documento = form.cleaned_data.get('TipoDocumento')
    linea = form.cleaned_data.get('Linea')
    cargo = form.cleaned_data.get('Cargo')
    certificaciones = form.cleaned_data.get('Certificación')
    perfil = form.cleaned_data.get('Perfil')

    if documento:
        empleados = empleados.filter(Documento=documento)
    if linea:
        empleados = empleados.filter(LineaId=linea)
    if cargo:
        empleados = empleados.filter(CargoId=cargo)
    if certificaciones:
        empleados = empleados.filter(Certificacion=certificaciones)
    if perfil:
        empleados = empleados.filter(PerfilId=perfil)

    return empleados

# Función para obtener la información del informe
def obtener_informe_empleados(queryset):
    """
    Genera el informe de empleados basado en un queryset dado.

    :param queryset: QuerySet filtrado de empleados.
    :return: Lista de diccionarios con los datos del informe.
    """
    campos = [
        'TipoDocumento', 'Documento', 'Nombre', 'FechaNacimiento', 'FechaIngreso', 'FechaOperacion',
        'ModuloId', 'PerfilId', 'LineaId', 'TituloProfesional', 'FechaGrado', 'Universidad',
        'ProfesionRealizada', 'TituloProfesionalActual', 'UniversidadActual', 'AcademiaSAP',
        'CertificadoSAP', 'OtrasCertificaciones', 'Postgrados'
    ]

    return list(queryset.values(*campos))

# Vista del informe de empleados
def informe_empleados(request):
    """
    Vista para generar el informe de empleados con filtros opcionales.
    """
    empleados_info = []
    show_data = False

    if request.method == 'GET':
        form = EmpleadoFilterForm(request.GET)

        if form.is_valid():
            empleados = Empleado.objects.all()

            # Aplicar filtros
            empleados = filtrar_empleados(form, empleados)

            # Obtener la información del informe solo si hay resultados
            if empleados.exists():
                empleados_info = obtener_informe_empleados(empleados)
                show_data = True

    else:
        form = EmpleadoFilterForm()

    context = {
        'form': form,
        'empleados_info': empleados_info,
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not show_data else ""
    }

    return render(request, 'informes/informes_empleado_index.html', context)


