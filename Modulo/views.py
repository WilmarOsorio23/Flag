from openpyxl import Workbook
import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
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


def inicio(request):
    return render(request, 'paginas/Inicio.html')

def nosotros(request):
    return render(request, 'paginas/nosotros.html')

# Vista para linea
def linea_index(request):
    linea_data = Linea.objects.all()
    return render(request, 'linea/linea_index.html', {'lineas': linea_data})

def linea_crear(request):
    if request.method == 'POST':
        form = LineaForm(request.POST)
        if form.is_valid():
            max_id = Linea.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nueva_linea = form.save(commit=False)
            nueva_linea.id = new_id
            nueva_linea.save()
            return redirect('linea_index')
    else:
        form = LineaForm()
    return render(request, 'linea/linea_form.html', {'form': form})

# Vista para editar una línea existente
def linea_editar(request, LineaId):
    linea = get_object_or_404(Linea, LineaId=LineaId)

    if request.method == 'POST':
        form = LineaForm(request.POST, instance=linea)
        if form.is_valid():
            form.save()
            return redirect('linea_index')
    else:
        form = LineaForm(instance=linea)

    return render(request, 'linea/linea_form.html', {'form': form})

# Vista para eliminar líneas seleccionadas
def linea_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Linea.objects.filter(LineaId__in=item_ids).delete()
        return redirect('linea_index')
    return redirect('linea_index')

# Vista para descargar líneas seleccionadas en Excel
def linea_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        linea_data = Linea.objects.filter(LineaId__in=item_ids)

        data = []
        for linea in linea_data:
            data.append([linea.LineaId, linea.Linea])

        df = pd.DataFrame(data, columns=['LineaId', 'Nombre'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="linea.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('linea_index')

# Vista perfil
def perfil_index(request):
    perfil_data = Perfil.objects.all()
    return render(request, 'perfil/perfil_index.html', {'perfil_data': perfil_data})


def perfil_crear(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST)
        if form.is_valid():
            # Si decides manejar el ID manualmente
            max_id = Perfil.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_perfil = form.save(commit=False)
            nuevo_perfil.id = new_id
            nuevo_perfil.save()
            return redirect('perfil_index')
    else:
        form = PerfilForm()
    return render(request, 'perfil/perfil_crear.html', {'form': form})


def perfil_editar(request, id):
    perfil = get_object_or_404(Perfil, id=id)

    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil_index')
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'perfil/perfil_form.html', {'form': form})


def perfil_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Perfil.objects.filter(id__in=item_ids).delete()
        return redirect('perfil_index')
    return redirect('perfil_index')

# Vista para descargar Perfiles seleccionados en formato Excel
def perfil_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        perfil_data = Perfil.objects.filter(id__in=item_ids)

        data = []
        for perfil in perfil_data:
            data.append([perfil.id, perfil.nombre])

        df = pd.DataFrame(data, columns=['Id', 'Nombre'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="perfil.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('perfil_index') 


# Vista para la tabla Consultores

def consultores_index(request):
    consultores = Consultores.objects.all()
    return render(request, 'consultores/consultores_index.html', {'consultores': consultores})

def consultores_crear(request):
    if request.method == 'POST':
        form = ConsultoresForm(request.POST)
        if form.is_valid():
            nuevo_consultor = form.save()
            return redirect('consultores_index')
    else:
        form = ConsultoresForm()
    
    return render(request, 'consultores/consultores_form.html', {'form': form})

@csrf_exempt
def consultores_editar(request, tipo_documento_id, documento_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            consultor = Consultores.objects.get(TipoDocumentoID=tipo_documento_id, DocumentoId=documento_id)
            form = ConsultoresForm(data, instance=consultor)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Consultores.DoesNotExist:
            return JsonResponse({'error': 'Consultor no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def consultores_eliminar(request):
    if request.method == 'POST':
        consultor_ids = request.POST.getlist('consultor_ids')
        for id_pair in consultor_ids:
            tipo_documento_id, documento_id = id_pair.split('-')
            Consultores.objects.filter(TipoDocumentoID=tipo_documento_id, DocumentoId=documento_id).delete()
        return redirect('consultores_index')
    return redirect('consultores_index')

def consultores_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_download', '').split(',')
        consultores_data = Consultores.objects.filter(TipoDocumentoID__in=item_ids)

        data = []
        for consultor in consultores_data:
            data.append([
                consultor.TipoDocumentoID,
                consultor.DocumentoId,
                consultor.Nombre,
                consultor.Empresa,
                consultor.Profesion,
                consultor.Estado,
                consultor.Fecha_Ingreso,
                consultor.Fecha_Retiro,
            ])

        df = pd.DataFrame(data, columns=[
            'Tipo Documento ID',
            'Documento ID',
            'Nombre',
            'Empresa',
            'Profesión',
            'Estado',
            'Fecha Ingreso',
            'Fecha Retiro'
        ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="consultores.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('consultores_index')


# Detalle gastos
def detalle_gastos_index(request):
    detalles = Detalle_Gastos.objects.all()
    print("Buscando plantilla en: Detalle_Gastos/detalle_gastos_index.html")
    return render(request, 'Detalle_Gastos/detalle_gastos_index.html', {'detalles': detalles})

def detalle_gastos_crear(request):
    if request.method == 'POST':
        form = DetalleGastosForm(request.POST)
        if form.is_valid():
            max_id = Detalle_Gastos.objects.all().aggregate(max_id=models.Max('GastosId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_detalle_gasto = form.save(commit=False)
            nuevo_detalle_gasto.GastosId = new_id
            nuevo_detalle_gasto.save()
            return redirect('detalle_gasto_index')
    else:
        form = DetalleGastosForm()
    return render(request, 'Detalle_Gastos/detalle_gastos_form.html', {'form': form})


def detalle_gastos_editar(request, Anio, Mes, GastosId):
    detalle = get_object_or_404(Detalle_Gastos, Anio=Anio, Mes=Mes, GastosId=GastosId)

    if request.method == 'POST':
        form = DetalleGastosForm(request.POST, instance=detalle)
        if form.is_valid():
            form.save()
            return redirect('detalle_gastos_index')
    else:
        form = DetalleGastosForm(instance=detalle)

    return render(request, 'Detalle_Gastos/detalle_gastos_form.html', {'form': form})

def detalle_gastos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        for item_id in item_ids:
            Anio, Mes, GastosId = item_id.split('-')
            Detalle_Gastos.objects.filter(Anio=Anio, Mes=Mes, GastosId=GastosId).delete()
        return redirect('detalle_gastos_index')
    return redirect('detalle_gastos_index')

def detalle_gastos_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        detalles = []
        for item_id in item_ids:
            Anio, Mes, GastosId = item_id.split('-')
            detalles.extend(Detalle_Gastos.objects.filter(Anio=Anio, Mes=Mes, GastosId=GastosId))

        data = []
        for detalle in detalles:
            data.append([detalle.Anio, detalle.Mes, detalle.GastosId, detalle.Valor])

        df = pd.DataFrame(data, columns=['Año', 'Mes', 'Gasto ID', 'Valor'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="detalle_gastos.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('detalle_gastos_index')

# Total gastos
def total_gastos_index(request):
    total_gastos_data = Total_Gastos.objects.all()
    return render(request, 'total_gastos/total_gastos_index.html', {'total_gastos_data': total_gastos_data})

def total_gastos_crear(request):
    if request.method == 'POST':
        form = TotalGastosForm(request.POST)
        if form.is_valid():
            max_id = Total_Gastos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_total_gasto = form.save(commit=False)
            nuevo_total_gasto.id = new_id  # Asignar un nuevo ID
            nuevo_total_gasto.save()
            return redirect('total_gasto_index')
    else:
        form = TotalGastosForm()
    return render(request, 'total_gastos/total_gastos_form.html', {'form': form})

def total_gastos_editar(request, anio, mes):
    total_gasto = get_object_or_404(Total_Gastos, anio=anio, mes=mes)

    if request.method == 'POST':
        form = TotalGastosForm(request.POST, instance=total_gasto)
        if form.is_valid():
            form.save()
            return redirect('total_gastos_index')
    else:
        form = TotalGastosForm(instance=total_gasto)

    return render(request, 'total_gastos/total_gastos_form.html', {'form': form})

def total_gastos_eliminar(request):
    if request.method == 'POST':
        items_to_delete = request.POST.getlist('items_to_delete')
        for item in items_to_delete:
            anio, mes = item.split('-')
            Total_Gastos.objects.filter(anio=anio, mes=mes).delete()
        return redirect('total_gastos_index')
    return redirect('total_gastos_index')

def total_gastos_descargar_excel(request):
    if request.method == 'POST':
        items_to_delete = request.POST.getlist('items_to_delete')
        total_gastos_data = []
        for item in items_to_delete:
            anio, mes = item.split('-')
            total_gastos_data.extend(Total_Gastos.objects.filter(anio=anio, mes=mes))

        data = [[tg.anio, tg.mes, tg.total] for tg in total_gastos_data]

        df = pd.DataFrame(data, columns=['Año', 'Mes', 'Total'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="total_gastos.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('total_gastos_index')

# Total costos indirectos
def total_costos_indirectos_index(request):
    total_costos_indirectos_data = Total_Costos_Indirectos.objects.all()
    return render(request, 'Total_Costos_Indirectos/total_costos_indirectos_index.html', {'total_costos_indirectos_data': total_costos_indirectos_data})


def total_costos_indirectos_crear(request):
    if request.method == 'POST':
        form = Total_Costos_IndirectosForm(request.POST)
        if form.is_valid():
            max_id = Total_Costos_Indirectos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_total_costo_indirecto = form.save(commit=False)
            nuevo_total_costo_indirecto.id = new_id  # Asignar un nuevo ID
            nuevo_total_costo_indirecto.save()
            return redirect('total_costos_indirectos_index')
    else:
        form = Total_Costos_IndirectosForm()
    return render(request, 'Total_Costos_Indirectos/total_costos_indirectos_form.html', {'form': form})


def total_costos_indirectos_editar(request, anio, mes):
    total_costos_indirectos = get_object_or_404(Total_Costos_Indirectos, anio=anio, mes=mes)
    if request.method == 'POST':
        form = Total_Costos_IndirectosForm(request.POST, instance=total_costos_indirectos)
        if form.is_valid():
            form.save()
            return redirect('total_costos_indirectos_index')
    else:
        form = Total_Costos_IndirectosForm(instance=total_costos_indirectos)
    return render(request, 'Total_Costos_Indirectos/total_costos_indirectos_form.html', {'form': form})

def total_costos_indirectos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        for item_id in item_ids:
            anio, mes = item_id.split('-')
            Total_Costos_Indirectos.objects.filter(anio=anio, mes=mes).delete()
        return redirect('total_costos_indirectos_index')
    return redirect('total_costos_indirectos_index')

def total_costos_indirectos_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        total_costos_indirectos_data = []
        for item_id in item_ids:
            anio, mes = item_id.split('-')
            item = get_object_or_404(Total_Costos_Indirectos, anio=anio, mes=mes)
            total_costos_indirectos_data.append([item.anio, item.mes, item.total])

        df = pd.DataFrame(total_costos_indirectos_data, columns=['Año', 'Mes', 'Total'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="total_costos_indirectos.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('total_costos_indirectos_index')

# Detalle costos indirectos
def detalle_costos_indirectos_index(request):
    detalle_data = Detalle_Costos_Indirectos.objects.all()
    return render(request, 'detalle_costos_indirectos/detalle_costos_indirectos_index.html', {'detalle_data': detalle_data})

def detalle_costos_indirectos_crear(request):
    if request.method == 'POST':
        form = DetalleCostosIndirectosForm(request.POST)
        if form.is_valid():
            max_id = Detalle_Costos_Indirectos.objects.all().aggregate(max_id=models.Max('CostoId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_detalle_costo_indirecto = form.save(commit=False)
            nuevo_detalle_costo_indirecto.CostoId = new_id  # Asignar un nuevo CostoId
            nuevo_detalle_costo_indirecto.save()
            return redirect('detalle_costos_indirectos_index')
    else:
        form = DetalleCostosIndirectosForm()
    return render(request, 'Total_Costos_Indirectos/total_costos_indirectos_form.html', {'form': form})

def detalle_costos_indirectos_editar(request, id):
    detalle = get_object_or_404(Detalle_Costos_Indirectos, id=id)

    if request.method == 'POST':
        form = DetalleCostosIndirectosForm(request.POST, instance=detalle)
        if form.is_valid():
            form.save()
            return redirect('detalle_costos_indirectos_index')
    else:
        form = DetalleCostosIndirectosForm(instance=detalle)

    return render(request, 'detalle_costos_indirectos/form.html', {'form': form})

def detalle_costos_indirectos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Detalle_Costos_Indirectos.objects.filter(id__in=item_ids).delete()
        return redirect('detalle_costos_indirectos_index')
    return redirect('detalle_costos_indirectos_index')

def detalle_costos_indirectos_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        detalle_data = Detalle_Costos_Indirectos.objects.filter(id__in=item_ids)

        data = []
        for detalle in detalle_data:
            data.append([detalle.id, detalle.anio, detalle.mes, detalle.costosid, detalle.valor])

        df = pd.DataFrame(data, columns=['Id', 'Año', 'Mes', 'Costos ID', 'Valor'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="detalle_costos_indirectos.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('detalle_costos_indirectos_index')

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

# Nomina
def nomina_index(request):
    nomina_data = Nomina.objects.all()
    return render(request, 'nomina/nomina_index.html', {'nomina_data': nomina_data})

def nomina_crear(request):
    if request.method == 'POST':
        form = NominaForm(request.POST)
        if form.is_valid():
            max_id = Nomina.objects.all().aggregate(max_id=models.Max('Documento'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nueva_nomina = form.save(commit=False)
            nueva_nomina.Documento = new_id  # Asignar un nuevo Documento
            nueva_nomina.save()
            return redirect('nomina_index')
    else:
        form = NominaForm()
    return render(request, 'Nomina/nomina_form.html', {'form': form})


def nomina_editar(request, anio, mes, documento):
    nomina = get_object_or_404(Nomina, anio=anio, mes=mes, documento=documento)

    if request.method == 'POST':
        form = NominaForm(request.POST, instance=nomina)
        if form.is_valid():
            form.save()
            return redirect('nomina_index')
    else:
        form = NominaForm(instance=nomina)

    return render(request, 'nomina/nomina_form.html', {'form': form})

def nomina_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        for item_id in item_ids:
            anio, mes, documento = item_id.split('|')
            Nomina.objects.filter(anio=anio, mes=mes, documento=documento).delete()
        return redirect('nomina_index')
    return redirect('nomina_index')

def nomina_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        nomina_data = []
        for item_id in item_ids:
            anio, mes, documento = item_id.split('|')
            nomina = Nomina.objects.filter(anio=anio, mes=mes, documento=documento).first()
            if nomina:
                nomina_data.append([nomina.anio, nomina.mes, nomina.documento, nomina.salario, nomina.cliente])

        df = pd.DataFrame(nomina_data, columns=['Año', 'Mes', 'Documento', 'Salario', 'Cliente'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="nomina.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('nomina_index')

# Detalle certificacion
def detalle_certificacion_index(request):
    detalles_certificacion = Detalle_Certificacion.objects.all()
    #print(detalles_certificacion) 
    return render(request, 'Detalle_Certificacion/detalle_certificacion_index.html', {'detalles_certificacion': detalles_certificacion})


def detalle_certificacion_crear(request):
    if request.method == 'POST':
        form = Detalle_CertificacionForm(request.POST)
        if form.is_valid():
            max_id = Detalle_Certificacion.objects.all().aggregate(max_id=models.Max('DocumentoId'))['max_id']
            if max_id is not None:
                try:
                    new_id = str(int(max_id) + 1)  
                except ValueError:
                    new_id = '1' 
            else:
                new_id = '1'
            nuevo_detalle_certificacion = form.save(commit=False)
            nuevo_detalle_certificacion.DocumentoId = new_id 
            nuevo_detalle_certificacion.save()
            return redirect('detalle_certificacion_index')
    else:
        form = Detalle_CertificacionForm()
    return render(request, 'Detalle_Certificacion/detalle_certificacion_form.html', {'form': form})

def detalle_certificacion_editar(request, documentoId, certificacionId):
    detalle_certificacion = get_object_or_404(Detalle_Certificacion, documentoId=documentoId, certificacionId=certificacionId)

    if request.method == 'POST':
        form = Detalle_CertificacionForm(request.POST, instance=detalle_certificacion)
        if form.is_valid():
            form.save()
            return redirect('detalle_certificacion_index')
    else:
        form = Detalle_CertificacionForm(instance=detalle_certificacion)

    return render(request, 'Detalle_Certificacion/detalle_certificacion_form.html', {'form': form})

def detalle_certificacion_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        for item_id in item_ids:
            documentoId, certificacionId = item_id.split('|')
            Detalle_Certificacion.objects.filter(documentoId=documentoId, certificacionId=certificacionId).delete()
        return redirect('detalle_certificacion_index')
    return redirect('detalle_certificacion_index')

def detalle_certificacion_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        detalles = []
        for item_id in item_ids:
            documentoId, certificacionId = item_id.split('|')
            detalle_certificacion = Detalle_Certificacion.objects.filter(documentoId=documentoId, certificacionId=certificacionId).first()
            if detalle_certificacion:
                detalles.append([detalle_certificacion.documentoId, detalle_certificacion.certificacionId, detalle_certificacion.fecha_certificacion])

        df = pd.DataFrame(detalles, columns=['Documento ID', 'Certificación ID', 'Fecha de Certificación'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="detalle_certificacion.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('detalle_certificacion_index')

# Vista para listar empleados
def empleado_index(request):
    empleados = Empleado.objects.all()
    return render(request, 'empleado/empleado_index.html', {'empleados': empleados})

# Vista para crear un nuevo empleado
def empleado_crear(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            max_id = Empleado.objects.all().aggregate(max_id=models.Max('Documento'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_empleado = form.save(commit=False)
            nuevo_empleado.Documento = new_id
            nuevo_empleado.save()

            return redirect('empleado_index')
    else:
        form = EmpleadoForm()
    
    return render(request, 'empleado/empleado_form.html', {'form': form})

# Vista para editar un empleado
@csrf_exempt
def empleado_editar(request, tipo_documento_id, documento_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            empleado = Empleado.objects.get(TipoDocumento=tipo_documento_id, Documento=documento_id)
            form = EmpleadoForm(data, instance=empleado)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Empleado.DoesNotExist:
            return JsonResponse({'error': 'Empleado no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para eliminar empleados
def empleado_eliminar(request):
    if request.method == 'POST':
        empleado_ids = request.POST.getlist('empleado_ids')
        for id_pair in empleado_ids:
            tipo_documento_id, documento_id = id_pair.split('-')
            Empleado.objects.filter(TipoDocumento=tipo_documento_id, Documento=documento_id).delete()
        return redirect('empleado_index')
    return redirect('empleado_index')

# Vista para descargar datos de empleados en Excel
def empleado_descargar_excel(request):
    if request.method == 'POST':
        # Obtener los IDs desde el formulario
        item_ids = request.POST.get('items_to_download', '').split(',')
        filter_params = []
        for item in item_ids:
            tipo_documento_id, documento_id = item.split('-')
            filter_params.append((tipo_documento_id, documento_id))

        empleados_data = Empleado.objects.filter(
            (Q(TipoDocumento=tipo_documento_id) & Q(Documento=documento_id)) for tipo_documento_id, documento_id in filter_params
        )

        data = []
        for empleado in empleados_data:
            data.append([
                empleado.TipoDocumento.Nombre, 
                empleado.Documento, 
                empleado.Nombre, 
                empleado.FechaIngreso, 
                empleado.FechaOperacion
            ])

        df = pd.DataFrame(data, columns=[
            'Tipo Documento', 
            'Documento ID', 
            'Nombre Empleado', 
            'Fecha Ingreso', 
            'Fecha Operación'
        ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="empleados.xlsx"'

        df.to_excel(response, index=False)
        return response

    return redirect('empleado_index')

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


# Funcionalidad para descargar los resultados en Excel
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

# Informe de Nómina de Empleados
def empleado_nomina_filtrado(request):
    empleados = Empleado.objects.all()  
    nominas = Nomina.objects.all()  
    empleado_info = None  
    show_data = False  

    if request.method == 'GET':
        form = EmpleadoFilterForm(request.GET)

        if form.is_valid():
            # Obtener los valores del formulario
            nombre = form.cleaned_data.get('Nombre')
            linea = form.cleaned_data.get('LineaId')
            modulo_id = form.cleaned_data.get('ModuloId')
            anio = form.cleaned_data.get('Anio')  
            mes = form.cleaned_data.get('Mes')
            cargo = form.cleaned_data.get('Cargo')  # Nuevo campo Cargo

            # Filtrar empleados
            if nombre:
                empleados = empleados.filter(Nombre__icontains=nombre)
            if linea:
                empleados = empleados.filter(LineaId=linea)
            if modulo_id:
                empleados = empleados.filter(ModuloId=modulo_id)
            if cargo:
                empleados = empleados.filter(Cargo__icontains=cargo)  # Aplicar filtro por cargo

            # Filtrar nóminas por año y mes
            if anio:
                nominas = nominas.filter(Anio=anio)
            if mes:
                nominas = nominas.filter(Mes=mes)

            # Filtrar nóminas por los empleados filtrados
            if empleados.exists():
                documentos_empleados = empleados.values_list('Documento', flat=True)
                nominas = nominas.filter(Documento__in=documentos_empleados)

            # Verificar si hay datos de nómina para los empleados filtrados
            if nominas.exists():
                empleado_info = []
                for empleado in empleados:
                    salarios = nominas.filter(Documento=empleado.Documento)
                    if salarios.exists():
                        for salario in salarios:
                            cliente = salario.Cliente
                            empleado_info.append({
                                'empleado': empleado,
                                'salario': salario.Salario,
                                'cliente': cliente, 
                                'anio': salario.Anio,
                                'mes': salario.Mes,
                            })
            show_data = True  

    else:
        form = EmpleadoFilterForm()

    context = {
        'form': form,
        'empleados': empleados,
        'nomina': nominas,
        'empleado_info': empleado_info,  
        'show_data': show_data,  
    }

    return render(request, 'informes/informes_salarios_index.html', context)




# Funcionalidad para descargar los resultados en Excel
def exportar_nomina_excel(request):
    empleados = Empleado.objects.all().select_related('LineaId', 'ModuloId', 'PerfilId').prefetch_related(
        Prefetch('nomina_set', queryset=Nomina.objects.select_related('Cliente')) # type: ignore
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Nómina de Empleados"
    ws.append([
         'Nombre', 'Línea', 'Módulo', 'Documento', 'Cargo', 'Perfil', 'Salario', 'Cliente', 'Año', 'Mes'
    ])

    for empleado in empleados:
        for nomina in empleado.nomina_set.all():
            ws.append([
                empleado.Nombre,
                empleado.LineaId.Nombre if empleado.LineaId else '',
                empleado.ModuloId.Nombre if empleado.ModuloId else '',
                empleado.Documento,
                empleado.Cargo,
                empleado.PerfilId.Nombre if empleado.PerfilId else '',
                nomina.Salario,
                nomina.Cliente.Nombre if nomina.Cliente else '',
                nomina.Anio,
                nomina.Mes
            ])

    response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') # type: ignore
    response['Content-Disposition'] = 'attachment; filename=empleados_nomina.xlsx'

    return response
