import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from .models import Modulo
from .forms import ModuloForm
from .models import IPC
from .forms import IPCForm
from .models import IND
from .forms import INDForm
from .models import Linea
from .forms import LineaForm
from .models import Perfil
from .forms import PerfilForm
from .models import TipoDocumento
from .forms import TipoDocumentoForm

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
            form.save()
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
        response['Content-Disposition'] = 'attachment; filename="modulos_seleccionados.xlsx"'

        df.to_excel(response, index=False)

        # Crea un escritor CSV
        writer = csv.writer(response)
        
        # Escribe el encabezado
        writer.writerow(['Id', 'Nombre módulo'])

        # Escribe los datos de los módulos
        for modulo in modulos:
            writer.writerow([modulo.id, modulo.Nombre])
        
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
            max_id = TipoDocumento.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_tipo_documento = form.save(commit=False)
            nuevo_tipo_documento.id = new_id
            nuevo_tipo_documento.save()
            return redirect('tipo_documento_index')
    else:
        form = TipoDocumentoForm()
    return render(request, 'Tipo_Documento/tipo_documento_form.html', {'form': form})

def tipo_documento_editar(request, id):
    tipo_documento = get_object_or_404(TipoDocumento, id=id)

    if request.method == 'POST':
        form = TipoDocumentoForm(request.POST, instance=tipo_documento)
        if form.is_valid():
            form.save()
            return redirect('tipo_documento_index')
    else:
        form = TipoDocumentoForm(instance=tipo_documento)

    return render(request, 'tipo_documento/tipo_documento_form.html', {'form': form})

def tipo_documento_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        TipoDocumento.objects.filter(id__in=item_ids).delete()
        return redirect('tipo_documento_index')
    return redirect('tipo_documento_index')

def tipo_documento_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        tipo_documento_data = TipoDocumento.objects.filter(id__in=item_ids)

        data = []
        for tipo_documento in tipo_documento_data:
            data.append([tipo_documento.id, tipo_documento.nombre, tipo_documento.descripcion])

        df = pd.DataFrame(data, columns=['Id', 'Nombre', 'Descripción'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="tipo_documento.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('tipo_documento_index')