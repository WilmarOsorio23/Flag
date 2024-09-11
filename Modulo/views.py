import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
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


def inicio(request):
    return render(request, 'paginas/Inicio.html')

def nosotros(request):
    return render(request, 'paginas/nosotros.html')

def Tablas(request):
    # Ordenar los módulos por el campo 'id' en orden ascendente
    modulos = Modulo.objects.all().order_by('id')
    return render(request, 'Tablas/index.html', {'modulos': modulos})


def crear(request):
    if request.method == 'POST':
        form = ModuloForm(request.POST)
        if form.is_valid():
            max_id = Modulo.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_modulo = form.save(commit=False)
            nuevo_modulo.id = new_id
            nuevo_modulo.save()
            
            return redirect('Tablas')
    else:
        form = ModuloForm()
    return render(request, 'Tablas/crear.html', {'form': form})

def editar(request, id):
    modulo = get_object_or_404(Modulo, pk=id)
    if request.method == 'POST':
        form = ModuloForm(request.POST, instance=modulo)
        if form.is_valid():
            form.save()
            return redirect('Tablas')
    else:
        form = ModuloForm(instance=modulo)
    return render(request, 'Tablas/editar.html', {'form': form})

def eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Modulo.objects.filter(id__in=item_ids).delete()
        return redirect('Tablas')
    return redirect('Tablas')

def descargar_excel(request):
    # Verifica si la solicitud es POST
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        modulos = Modulo.objects.filter(id__in=item_ids)
        
        # Crea una respuesta HTTP con el tipo de contenido de CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="modulos_seleccionados.csv"'



        data = []
        for modulo in modulos:
            data.append([modulo.id, modulo.Nombre])

        df = pd.DataFrame(data, columns=['Id', 'Nombre'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Modulos.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('Tablas')

# Vista para la tabla IPC
def ipc_index(request):
    ipc_data = IPC.objects.all()
    return render(request, 'ipc/ipc_index.html', {'ipc_data': ipc_data})

def ipc_crear(request):
    if request.method == 'POST':
        form = IPCForm(request.POST)
        if form.is_valid():
            max_id = IPC.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_ipc = form.save(commit=False)
            nuevo_ipc.id = new_id
            nuevo_ipc.save()
            return redirect('ipc_index')
    else:
        form = IPCForm()
    return render(request, 'ipc/ipc_form.html', {'form': form})

def ipc_editar(request, id):
    ipc = get_object_or_404(IPC, id=id)

    if request.method == 'POST':
        form = IPCForm(request.POST, instance=ipc)
        if form.is_valid():
            ipc = form.save(commit=False)
            ipc.anio = ipc.anio
            ipc.mes = ipc.mes
            ipc.save()
            return redirect('ipc_index')
    else:
        form = IPCForm(instance=ipc)

    return render(request, 'ipc/ipc_form.html', {'form': form})

def ipc_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        IPC.objects.filter(id__in=item_ids).delete()
        return redirect('ipc_index')
    return redirect('ipc_index')

def ipc_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        ipc_data = IPC.objects.filter(id__in=item_ids)

        data = []
        for ipc in ipc_data:
            data.append([ipc.id, ipc.anio, ipc.mes, ipc.campo_numerico])

        df = pd.DataFrame(data, columns=['Id', 'Año', 'Mes', 'Campo Numérico'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="ipc.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('ipc_index')

#vista para la IND

def ind_index(request):
    ind_data = IND.objects.all()
    return render(request, 'ind/ind_index.html', {'ind_data': ind_data})

def ind_crear(request):
    if request.method == 'POST':
        form = INDForm(request.POST)
        if form.is_valid():
            max_id = IND.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_ind = form.save(commit=False)
            nuevo_ind.id = new_id
            nuevo_ind.save()
            return redirect('ind_index')
    else:
        form = INDForm()
    return render(request, 'ind/ind_form.html', {'form': form})

def ind_editar(request, id):
    ind = get_object_or_404(IND, id=id)

    if request.method == 'POST':
        form = INDForm(request.POST, instance=ind)
        if form.is_valid():
            ind = form.save(commit=False)
            ind.anio = ind.anio
            ind.mes = ind.mes
            ind.save()
            return redirect('ind_index')
    else:
        form = INDForm(instance=ind)

    return render(request, 'ind/ind_form.html', {'form': form})

def ind_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        IND.objects.filter(id__in=item_ids).delete()
        return redirect('ind_index')
    return redirect('ind_index')

def ind_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        ind_data = IND.objects.filter(id__in=item_ids)

        data = []
        for ind in ind_data:
            data.append([ind.id, ind.anio, ind.mes, ind.campo_numerico])

        df = pd.DataFrame(data, columns=['Id', 'Año', 'Mes', 'Campo Numérico'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="ind.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('ind_index')

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

def linea_editar(request, id):
    linea = get_object_or_404(Linea, id=id)

    if request.method == 'POST':
        form = LineaForm(request.POST, instance=linea)
        if form.is_valid():
            form.save()
            return redirect('linea_index')
    else:
        form = LineaForm(instance=linea)

    return render(request, 'linea/linea_form.html', {'form': form})

def linea_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Linea.objects.filter(id__in=item_ids).delete()
        return redirect('linea_index')
    return redirect('linea_index')

def linea_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        linea_data = Linea.objects.filter(id__in=item_ids)

        data = []
        for linea in linea_data:
            data.append([linea.id, linea.nombre, linea.descripcion])

        df = pd.DataFrame(data, columns=['Id', 'Nombre', 'Descripción'])

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

# Vista Tipo Documento
def tipo_documento_index(request):
    tipo_documentos = TipoDocumento.objects.all()
    return render(request, 'Tipo_Documento/tipo_documento_index.html', {'tipo_documentos': tipo_documentos})

def tipo_documento_crear(request):
    if request.method == 'POST':
        form = TipoDocumentoForm(request.POST)
        if form.is_valid():
            # Obtener el valor máximo actual de TipoDocumentoID
            max_id = TipoDocumento.objects.all().aggregate(max_id=models.Max('TipoDocumentoID'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_tipo_documento = form.save(commit=False)
            nuevo_tipo_documento.TipoDocumentoID = new_id  # Asignar manualmente el nuevo ID
            nuevo_tipo_documento.save()
            return redirect('tipo_documento_index')
    else:
        form = TipoDocumentoForm()
    return render(request, 'Tipo_Documento/tipo_documento_form.html', {'form': form})

def tipo_documento_editar(request, TipoDocumentoID):
    tipo_documento = get_object_or_404(TipoDocumento, TipoDocumentoID=TipoDocumentoID)

    if request.method == 'POST':
        form = TipoDocumentoForm(request.POST, instance=tipo_documento)
        if form.is_valid():
            form.save()
            return redirect('tipo_documento_index')
    else:
        form = TipoDocumentoForm(instance=tipo_documento)

    return render(request, 'Tipo_Documento/tipo_documento_form.html', {'form': form})

def tipo_documento_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        TipoDocumento.objects.filter(TipoDocumentoID__in=item_ids).delete()
        return redirect('tipo_documento_index')
    return redirect('tipo_documento_index')

def tipo_documento_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        tipo_documento_data = TipoDocumento.objects.filter(TipoDocumentoID__in=item_ids)

        data = []
        for tipo_documento in tipo_documento_data:
            data.append([tipo_documento.TipoDocumentoID, tipo_documento.Nombre])

        df = pd.DataFrame(data, columns=['TipoDocumentoID', 'Nombre'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="tipo_documento.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('tipo_documento_index')

# Vista para la tabla Clientes
def clientes_index(request):
    clientes = Clientes.objects.all()
    return render(request, 'clientes/clientes_index.html', {'clientes': clientes})

def clientes_crear(request):
    if request.method == 'POST':
        form = ClientesForm(request.POST)
        if form.is_valid():
            max_id = Clientes.objects.all().aggregate(max_id=models.Max('ClienteId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_cliente = form.save(commit=False)
            nuevo_cliente.ClienteId = new_id
            nuevo_cliente.save()
            return redirect('clientes_index')
    else:
        form = ClientesForm()
    
    return render(request, 'clientes/clientes_form.html', {'form': form})


@csrf_exempt
def clientes_editar(request, tipo_documento_id, documento_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            cliente = Clientes.objects.get(TipoDocumentoID=tipo_documento_id, DocumentoId=documento_id)
            form = ClientesForm(data, instance=cliente)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Clientes.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def clientes_eliminar(request):
    if request.method == 'POST':
        cliente_ids = request.POST.getlist('cliente_ids')
        for id_pair in cliente_ids:
            tipo_documento_id, documento_id = id_pair.split('-')
            Clientes.objects.filter(TipoDocumentoID=tipo_documento_id, DocumentoId=documento_id).delete()
        return redirect('clientes_index')
    return redirect('clientes_index')

def clientes_descargar_excel(request):
    if request.method == 'POST':
        # Obtener los IDs desde el formulario
        item_ids = request.POST.get('items_to_download', '').split(',')
        
        # Crear una lista para almacenar las combinaciones de TipoDocumentoID y DocumentoId
        filter_params = []
        for item in item_ids:
            tipo_documento_id, documento_id = item.split('-')
            filter_params.append((tipo_documento_id, documento_id))
        
        # Filtrar los clientes usando las combinaciones
        clientes_data = Clientes.objects.filter(
            (Q(TipoDocumentoID=tipo_documento_id) & Q(DocumentoId=documento_id)) for tipo_documento_id, documento_id in filter_params
        )

        # Preparar los datos para el DataFrame
        data = []
        for cliente in clientes_data:
            data.append([
                cliente.TipoDocumentoID.Nombre,  # Asumiendo que quieres mostrar el nombre del tipo de documento
                cliente.DocumentoId, 
                cliente.Nombre_Cliente, 
                cliente.Activo, 
                cliente.Fecha_Inicio, 
                cliente.Fecha_Retiro
            ])

        # Crear el DataFrame y exportar a Excel
        df = pd.DataFrame(data, columns=[
            'Tipo Documento', 
            'Documento ID', 
            'Nombre Cliente', 
            'Activo', 
            'Fecha Inicio', 
            'Fecha Retiro'
        ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="clientes.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('cliente_index')


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

# Vista Certificacion
def certificacion_index(request):
    certificaciones = Certificacion.objects.all()
    return render(request, 'Certificacion/certificacion_index.html', {'certificaciones': certificaciones})

def certificacion_crear(request):
    if request.method == 'POST':
        form = CertificacionForm(request.POST)
        if form.is_valid():
            max_id = Certificacion.objects.all().aggregate(max_id=models.Max('CertificacionId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nueva_certificacion = form.save(commit=False)
            nueva_certificacion.CertificacionId = new_id
            nueva_certificacion.save()
            return redirect('certificacion_index')
    else:
        form = CertificacionForm()
    return render(request, 'Certificacion/certificacion_form.html', {'form': form})

def certificacion_editar(request, id):
    certificacion = get_object_or_404(Certificacion, CertificacionId=id)

    if request.method == 'POST':
        form = CertificacionForm(request.POST, instance=certificacion)
        if form.is_valid():
            form.save()
            return redirect('certificacion_index')
    else:
        form = CertificacionForm(instance=certificacion)

    return render(request, 'Certificacion/certificacion_form.html', {'form': form})

def certificacion_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Certificacion.objects.filter(CertificacionId__in=item_ids).delete()
        return redirect('certificacion_index')
    return redirect('certificacion_index')

def certificacion_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        certificacion_data = Certificacion.objects.filter(CertificacionId__in=item_ids)

        data = []
        for certificacion in certificacion_data:
            data.append([certificacion.CertificacionId, certificacion.Certificacion])

        df = pd.DataFrame(data, columns=['Id Certificación', 'Certificación'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="certificaciones.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('certificacion_index')

# Vista Costo Indirecto
def costos_indirectos_index(request):
    costos_indirectos = Costos_Indirectos.objects.all()
    return render(request, 'Costos_Indirectos/costos_indirecto_index.html', {'costos_indirectos': costos_indirectos})

def costos_indirectos_crear(request):
    if request.method == 'POST':
        form = CostosIndirectosForm(request.POST)
        if form.is_valid():
            max_id = Costos_Indirectos.objects.all().aggregate(max_id=models.Max('CostoId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_costo = form.save(commit=False)
            nuevo_costo.CostoId = new_id
            nuevo_costo.save()
            return redirect('costos_indirectos_index')
    else:
        form = CostosIndirectosForm()
    return render(request, 'Costos_Indirectos/costos_indirectos_form.html', {'form': form})

def costos_indirectos_editar(request, id):
    costo = get_object_or_404(Costos_Indirectos, CostoId=id)

    if request.method == 'POST':
        form = CostosIndirectosForm(request.POST, instance=costo)
        if form.is_valid():
            form.save()
            return redirect('costos_indirectos_index')
    else:
        form = CostosIndirectosForm(instance=costo)

    return render(request, 'Costos_Indirectos/costos_indirectos_form.html', {'form': form})

def costos_indirectos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Costos_Indirectos.objects.filter(CostoId__in=item_ids).delete()
        return redirect('costos_indirectos_index')
    return redirect('costos_indirectos_index')

def costos_indirectos_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        costos_data = Costos_Indirectos.objects.filter(CostoId__in=item_ids)

        data = []
        for costo in costos_data:
            data.append([costo.CostoId, costo.Costo])

        df = pd.DataFrame(data, columns=['CostoId', 'Costo'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="costos_indirectos.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('costos_indirectos_index')


# Conceptos
def conceptos_index(request):
    conceptos = Conceptos.objects.all()
    return render(request, 'Conceptos/conceptos_index.html', {'conceptos': conceptos})

def conceptos_crear(request):
    if request.method == 'POST':
        form = ConceptoForm(request.POST)
        if form.is_valid():
            max_id = Conceptos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_concepto = form.save(commit=False)
            nuevo_concepto.id = new_id
            nuevo_concepto.save()
            return redirect('conceptos_index')
    else:
        form = ConceptoForm()
    return render(request, 'Conceptos/conceptos_form.html', {'form': form})

def conceptos_editar(request, id):
    concepto = get_object_or_404(Conceptos, id=id)

    if request.method == 'POST':
        form = ConceptoForm(request.POST, instance=concepto)
        if form.is_valid():
            form.save()
            return redirect('conceptos_index')
    else:
        form = ConceptoForm(instance=concepto)

    return render(request, 'Conceptos/conceptos_form.html', {'form': form})

def conceptos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Conceptos.objects.filter(id__in=item_ids).delete()
        return redirect('conceptos_index')
    return redirect('conceptos_index')

def conceptos_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        concepto_data = Conceptos.objects.filter(id__in=item_ids)

        data = []
        for concepto in concepto_data:
            data.append([concepto.id, concepto.descripcion])

        df = pd.DataFrame(data, columns=['Id', 'Descripción'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="conceptos.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('conceptos_index')

# Vista Gastos
def gasto_index(request):
    gastos = Gastos.objects.all()
    return render(request, 'Gastos/gasto_index.html', {'gastos': gastos})

def gasto_crear(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            max_id = Gastos.objects.all().aggregate(max_id=models.Max('GastoId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_gasto = form.save(commit=False)
            nuevo_gasto.GastoId = new_id
            nuevo_gasto.save()
            return redirect('gasto_index')
    else:
        form = GastoForm()
    return render(request, 'Gastos/gasto_form.html', {'form': form})

def gasto_editar(request, id):
    gasto = get_object_or_404(Gastos, GastoId=id)

    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            return redirect('gastos_index')
    else:
        form = GastoForm(instance=gasto)

    return render(request, 'Gastos/gastos_form.html', {'form': form})

def gasto_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Gastos.objects.filter(GastoId__in=item_ids).delete()
        return redirect('gastos_index')
    return redirect('gastos_index')

def gasto_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        gasto_data = Gastos.objects.filter(GastoId__in=item_ids)

        data = []
        for gasto in gasto_data:
            data.append([gasto.GastoId, gasto.Gasto])

        df = pd.DataFrame(data, columns=['GastoId', 'Gasto'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="gastos.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('gastos_index')

# Detalle gastos
def detalle_gastos_index(request):
    detalles = Detalle_Gastos.objects.all()
    print("Buscando plantilla en: Detalle_Gastos/detalle_gastos_index.html")
    return render(request, 'Detalle_Gastos/detalle_gastos_index.html', {'detalles': detalles})

def detalle_gastos_crear(request):
    if request.method == 'POST':
        form = DetalleGastosForm(request.POST)
        if form.is_valid():
            # No necesitas generar un ID, ya que Anio, Mes, y GastoId son parte de la clave primaria
            nuevo_detalle_gasto = form.save(commit=False)
            nuevo_detalle_gasto.save()
            return redirect('detalle_gastos_index')
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
            # No necesitas generar un ID, ya que Anio y Mes son claves primarias
            nuevo_total_gasto = form.save(commit=False)
            nuevo_total_gasto.save()
            return redirect('total_gastos_index')
    else:
        form = TotalGastosForm()
    return render(request, 'Total_Gastos/total_gastos_form.html', {'form': form})

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
            # No necesitas generar un ID, ya que Anio y Mes son parte de la clave primaria
            nuevo_total_costo_indirecto = form.save(commit=False)
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
            nuevo_detalle_costo_indirecto = form.save(commit=False)
            nuevo_detalle_costo_indirecto.save()
            return redirect('detalle_costos_indirectos_index')
    else:
        form = DetalleCostosIndirectosForm()
    return render(request, 'Detalle_Costos_Indirectos/detalle_costos_indirectos_form.html', {'form': form})

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
            nuevo_tiempo_concepto = form.save(commit=False)
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
            nuevo_tiempo_cliente = form.save(commit=False)
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
            nueva_nomina = form.save(commit=False)
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
    return render(request, 'Detalle_Certificacion/detalle_certificacion_index.html', {'detalles_certificacion': detalles_certificacion})


def detalle_certificacion_crear(request):
    if request.method == 'POST':
        form = Detalle_CertificacionForm(request.POST)
        if form.is_valid():
            nuevo_detalle_certificacion = form.save(commit=False)
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