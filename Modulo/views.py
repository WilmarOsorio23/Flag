from openpyxl import Workbook
import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.db.models import Q
from django.contrib import messages
from .models import Modulo
from .forms import ModuloForm
from .models import IPC
from .models import Clientes
from .forms import IPCForm
from .models import IND
from .forms import INDForm
from .models import Linea
from .forms import LineaForm
from .models import Perfil
from .forms import PerfilForm
from .models import TipoDocumento
from .forms import TipoDocumentoForm
from .forms import ClientesForm
from .models import Consultores
from .forms import ConsultoresForm
from .models import Certificacion
from .forms import CertificacionForm
from .models import Concepto
from .forms import ConceptoForm
from .models import Costos_Indirectos
from .forms import CostosIndirectosForm
from .models import Gastos
from .forms import GastoForm
from .models import Detalle_Gastos
from .forms import DetalleGastosForm
from .models import Total_Gastos
from .forms import TotalGastosForm
from .models import Total_Costos_Indirectos
from .forms import Total_Costos_IndirectosForm
from .models import Detalle_Costos_Indirectos
from .forms import DetalleCostosIndirectosForm
from .models import TiemposConcepto
from .forms import TiemposConceptoForm
from .models import Tiempos_Cliente
from .forms import Tiempos_ClienteForm
from .models import Nomina
from .forms import NominaForm
from .models import Detalle_Certificacion
from .forms import Detalle_CertificacionForm
from .models import Empleado
from .forms import EmpleadoForm
from .forms import EmpleadoFilterForm
from .models import TiposContactos
from .forms import TiposContactosForm
from .models import Contactos
from .forms import ContactosForm
from .models import Historial_Cargos
from .forms import HistorialCargosForm
from .models import Moneda
from .forms import MonedaForm
from .models import ClientesContratos
from .forms import ClientesContratosForm

def inicio(request):
    return render(request, 'paginas/Inicio.html')

def nosotros(request):
    return render(request, 'paginas/nosotros.html')

# Tiempos concepto
def tiempos_concepto_index(request):
    tiempos_data = TiemposConcepto.objects.all()
    return render(request, 'tiempos_concepto/tiempos_concepto_index.html', {'tiempos_data': tiempos_data})

def tiempos_concepto_crear(request):
    if request.method == 'POST':
        form = TiemposConceptoForm(request.POST)
        if form.is_valid():
            max_id = TiemposConcepto.objects.all().aggregate(max_id=models.Max('ConceptoId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_tiempo_concepto = form.save(commit=False)
            nuevo_tiempo_concepto.ConceptoId = new_id  # Asignar un nuevo ConceptoId
            nuevo_tiempo_concepto.save()
            return redirect('tiempos_concepto_index')
    else:
        form = TiemposConceptoForm()
    return render(request, 'Tiempos_Concepto/tiempos_concepto_form.html', {'form': form})

def tiempos_concepto_editar(request, id):
    tiempos_concepto = get_object_or_404(TiemposConcepto, id=id)

    if request.method == 'POST':
        form = TiemposConceptoForm(request.POST, instance=tiempos_concepto)
        if form.is_valid():
            form.save()
            return redirect('tiempos_concepto_index')
    else:
        form = TiemposConceptoForm(instance=tiempos_concepto)

    return render(request, 'tiempos_concepto/tiempos_concepto_form.html', {'form': form})

def tiempos_concepto_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        TiemposConcepto.objects.filter(id__in=item_ids).delete()
        return redirect('tiempos_concepto_index')
    return redirect('tiempos_concepto_index')

def tiempos_concepto_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        tiempos_data = TiemposConcepto.objects.filter(id__in=item_ids)

        data = []
        for tiempo in tiempos_data:
            data.append([tiempo.anio, tiempo.mes, tiempo.colaborador, tiempo.concepto_id, tiempo.horas])

        df = pd.DataFrame(data, columns=['Año', 'Mes', 'Colaborador', 'Concepto', 'Horas'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="tiempos_concepto.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('tiempos_concepto_index')

# Tiempos cliente
def tiempos_cliente_index(request):
    tiempos_cliente_data = Tiempos_Cliente.objects.all()
    return render(request, 'tiempos_cliente/tiempos_cliente_index.html', {'tiempos_cliente_data': tiempos_cliente_data})

def tiempos_cliente_crear(request):
    if request.method == 'POST':
        form = Tiempos_ClienteForm(request.POST)
        if form.is_valid():
            max_id = Tiempos_Cliente.objects.all().aggregate(max_id=models.Max('ClienteId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_tiempo_cliente = form.save(commit=False)
            nuevo_tiempo_cliente.ClienteId = new_id  # Asignar un nuevo ClienteId
            nuevo_tiempo_cliente.save()
            return redirect('tiempos_cliente_index')
    else:
        form = Tiempos_ClienteForm()
    return render(request, 'Tiempos_Cliente/tiempos_cliente_form.html', {'form': form})

def tiempos_cliente_editar(request, anio, mes, colaborador, cliente_id):
    tiempo_cliente = get_object_or_404(Tiempos_Cliente, anio=anio, mes=mes, colaborador=colaborador, cliente_id=cliente_id)

    if request.method == 'POST':
        form = Tiempos_ClienteForm(request.POST, instance=tiempo_cliente)
        if form.is_valid():
            form.save()
            return redirect('tiempos_cliente_index')
    else:
        form = Tiempos_ClienteForm(instance=tiempo_cliente)

    return render(request, 'tiempos_cliente/tiempos_cliente_form.html', {'form': form})

def tiempos_cliente_eliminar(request):
    if request.method == 'POST':
        ids_to_delete = request.POST.getlist('items_to_delete')
        Tiempos_Cliente.objects.filter(id__in=ids_to_delete).delete()
    return redirect('tiempos_cliente_index')

def tiempos_cliente_descargar_excel(request):
    tiempos_cliente_data = Tiempos_Cliente.objects.all()
    data = []
    for tiempo_cliente in tiempos_cliente_data:
        data.append([
            tiempo_cliente.anio,
            tiempo_cliente.mes,
            tiempo_cliente.colaborador,
            tiempo_cliente.cliente_id,
            tiempo_cliente.horas
        ])
    df = pd.DataFrame(data, columns=['Año', 'Mes', 'Colaborador', 'Cliente ID', 'Horas'])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="tiempos_cliente.xlsx"'
    
    df.to_excel(response, index=False)
    
    return response




# Informe de Certificación de Empleados
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

    return response






















