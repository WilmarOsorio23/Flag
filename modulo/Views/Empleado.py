# Vista para listar empleados
import json
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, F, Func, Value
import pandas as pd
from modulo.forms import EmpleadoForm, EmpleadoIndexFilterForm
from modulo.models import Empleado, Nomina
from django.views.decorators.csrf import csrf_exempt
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_empleados')
def empleado_index(request):
    empleados = Empleado.objects.select_related(
        'TipoDocumento', 'ModuloId', 'PerfilId', 'LineaId', 'CargoId'
    ).all()
    filter_form = EmpleadoIndexFilterForm(request.GET or None)
    if filter_form.is_valid():
        q = (filter_form.cleaned_data.get('q') or '').strip()
        if q:
            empleados = empleados.filter(
                Q(Nombre__icontains=q) | Q(Documento__icontains=q)
            )
        if filter_form.cleaned_data.get('LineaId'):
            empleados = empleados.filter(LineaId=filter_form.cleaned_data['LineaId'])
        if filter_form.cleaned_data.get('CargoId'):
            empleados = empleados.filter(CargoId=filter_form.cleaned_data['CargoId'])
        if filter_form.cleaned_data.get('PerfilId'):
            empleados = empleados.filter(PerfilId=filter_form.cleaned_data['PerfilId'])
        if filter_form.cleaned_data.get('ModuloId'):
            empleados = empleados.filter(ModuloId=filter_form.cleaned_data['ModuloId'])
        act = filter_form.cleaned_data.get('Activo')
        if act == '1':
            empleados = empleados.filter(Activo=True)
        elif act == '0':
            empleados = empleados.filter(Activo=False)
    form = EmpleadoForm()
    return render(request, 'Empleado/EmpleadoIndex.html', {
        'empleados': empleados,
        'form': form,
        'filter_form': filter_form,
    })

@login_required
@verificar_permiso('can_manage_empleados')
def empleado_crear(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            nuevo_empleado = form.save(commit=False)
            nuevo_empleado.save()
            return redirect('empleado_index')
    else:
        form = EmpleadoForm()
    
    return render(request, 'Empleado/EmpleadoForm.html', {'form': form})

@login_required
@verificar_permiso('can_manage_empleados')
@csrf_exempt
def empleado_editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            # Normalizar campos opcionales enviados desde el front
            if data.get('PerfilId') == '':
                data['PerfilId'] = None
            if data.get('TarjetaProfesional') == '':
                data['TarjetaProfesional'] = None
            elif data.get('TarjetaProfesional') == '1':
                data['TarjetaProfesional'] = True
            elif data.get('TarjetaProfesional') == '0':
                data['TarjetaProfesional'] = False
            if data.get('NumeroHijos') == '':
                data['NumeroHijos'] = None
            empleado = get_object_or_404(Empleado, Documento=id)
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

@login_required
@verificar_permiso('can_manage_empleados')
def empleado_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Empleado.objects.filter(Documento__in=item_ids).delete()
        messages.success(request, 'Los Empleados seleccionados se han eliminado correctamente.')
        return redirect('empleado_index')
    return redirect('empleado_index')

@login_required
@verificar_permiso('can_manage_empleados')
def verificar_relaciones(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])

            # Verifica si los módulos están relacionados
            relacionados = []
            for id in ids:
                is_related = Nomina.objects.filter(Documento=id).exists()
                if is_related:
                    relacionados.append(id)

            if relacionados:
                return JsonResponse({
                    'isRelated': True,
                    'ids': relacionados
                })
            else:
                return JsonResponse({'isRelated': False})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_empleados')
def empleado_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete')
        documentos = item_ids.split(',')

        # Eliminar puntos de los documentos recibidos
        documentos_limpios = [doc.replace('.', '') for doc in documentos]

        # Comparar documentos en la BD eliminando puntos antes de filtrar
        empleados_data = Empleado.objects.annotate(
            DocumentoSinPuntos=Func(F('Documento'), Value('.'), Value(''), function='REPLACE')
        ).filter(DocumentoSinPuntos__in=documentos_limpios)

        # Preparar respuesta en formato Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="empleados.xlsx"'

        # Extraer los datos en formato lista para el DataFrame
        def perfil_str(e):
            return e.PerfilId.Perfil if e.PerfilId_id else 'N/A'

        data = [
            [
                empleado.TipoDocumento.Nombre,
                empleado.Documento,
                empleado.Nombre,
                empleado.FechaNacimiento,
                empleado.FechaIngreso,
                empleado.FechaOperacion,
                empleado.ModuloId,
                perfil_str(empleado),
                empleado.LineaId,
                empleado.CargoId,
                empleado.TituloProfesional,
                empleado.FechaGrado,
                empleado.Universidad,
                empleado.ProfesionRealizada,
                empleado.AcademiaSAP,
                empleado.CertificadoSAP,
                empleado.OtrasCertificaciones,
                empleado.Postgrados,
                empleado.Activo,
                getattr(empleado, 'Genero', None) or '',
                getattr(empleado, 'EstadoCivil', None) or '',
                getattr(empleado, 'NumeroHijos', None),
                'Sí' if getattr(empleado, 'TarjetaProfesional', None) else ('No' if getattr(empleado, 'TarjetaProfesional', None) is False else ''),
                getattr(empleado, 'RH', None) or '',
                getattr(empleado, 'TipoContrato', None) or '',
                getattr(empleado, 'FondoPension', None) or '',
                getattr(empleado, 'EPS', None) or '',
                getattr(empleado, 'FondoCesantias', None) or '',
                getattr(empleado, 'CajaCompensacion', None) or '',
                empleado.FechaRetiro,
                empleado.Direccion,
                empleado.Ciudad,
                empleado.Departamento,
                empleado.DireccionAlterna,
                empleado.Telefono1,
                empleado.Telefono2,
            ]
            for empleado in empleados_data
        ]

        df = pd.DataFrame(data, columns=[
            'Tipo Documento', 'Documento ID', 'Nombre Empleado', 'Fecha Nacimiento', 'Fecha Ingreso',
            'Fecha Operación', 'ID Módulo', 'Perfil', 'ID Línea', 'Cargo', 'Título Profesional',
            'Fecha Grado', 'Universidad', 'Profesión Realizada', 'Academia SAP', 'Certificado SAP',
            'Otras Certificaciones', 'Postgrados', 'Activo',
            'Género', 'Estado civil', 'Nº hijos', 'Tarjeta profesional', 'RH', 'Tipo contrato',
            'Fondo pensión', 'EPS', 'Fondo cesantías', 'Caja compensación',
            'Fecha Retiro', 'Dirección', 'Ciudad', 'Departamento', 'Dirección Alterna', 'Telefono 1', 'Telefono 2',
        ])

        df.to_excel(response, index=False)
        return response

    return redirect('empleado_index')