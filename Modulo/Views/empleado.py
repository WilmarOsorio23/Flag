# Vista para listar empleados
import json
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo.forms import EmpleadoForm
from Modulo.models import Empleado, Nomina
from django.views.decorators.csrf import csrf_exempt

def empleado_index(request):
    empleados = Empleado.objects.all()
    form = EmpleadoForm()
    return render(request, 'empleado/empleado_index.html', {'empleados': empleados, 'form': form})

# Vista para crear un nuevo empleado
def empleado_crear(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            nuevo_empleado = form.save(commit=False)
            nuevo_empleado.save()

            return redirect('empleado_index')
    else:
        form = EmpleadoForm()
    
    return render(request, 'empleado/empleado_form.html', {'form': form})

# Vista para editar un empleado
@csrf_exempt
def empleado_editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
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

# Vista para eliminar empleados
def empleado_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Empleado.objects.filter(Documento__in=item_ids).delete()
        messages.success(request, 'Los Empleados seleccionados se han eliminado correctamente.')
        return redirect('empleado_index')
    return redirect('empleado_index')

def verificar_relaciones(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])

            # Verifica si los módulos están relacionados
            relacionados = []
            for id in ids:
                # Verifica si el empleado está relacionado con la nómina
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

# Vista para descargar datos de empleados en Excel
def empleado_descargar_excel(request):
    if request.method == 'POST':
        
        # Obtener los IDs desde el formulario
        item_ids = request.POST.get('items_to_delete') 
        item_ids = list(map(int, item_ids.split (',')))  # Cambiado aquí

        empleados_data = Empleado.objects.filter(Documento__in=item_ids)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="empleados.xlsx"'

        data = []
        for empleado in empleados_data:
            data.append([
                empleado.TipoDocumento.Nombre, 
                empleado.Documento, 
                empleado.Nombre, 
                empleado.FechaNacimiento, 
                empleado.FechaIngreso, 
                empleado.FechaOperacion, 
                empleado.ModuloId, 
                empleado.PerfilId, 
                empleado.LineaId, 
                empleado.CargoId, 
                empleado.TituloProfesional, 
                empleado.FechaGrado, 
                empleado.Universidad, 
                empleado.ProfesionRealizada, 
                empleado.TituloProfesionalActual, 
                empleado.UniversidadActual, 
                empleado.AcademiaSAP, 
                empleado.CertificadoSAP, 
                empleado.OtrasCertificaciones, 
                empleado.Postgrados
            ])

        df = pd.DataFrame(data, columns=[
            'Tipo Documento', 
            'Documento ID', 
            'Nombre Empleado', 
            'Fecha Nacimiento', 
            'Fecha Ingreso', 
            'Fecha Operación', 
            'ID Módulo', 
            'ID Perfil', 
            'ID Línea', 
            'Cargo', 
            'Título Profesional', 
            'Fecha Grado', 
            'Universidad', 
            'Profesión Realizada', 
            'Título Profesional Actual', 
            'Universidad Actual', 
            'Academia SAP', 
            'Certificado SAP', 
            'Otras Certificaciones', 
            'Postgrados'
        ])

        df.to_excel(response, index=False)
        return response

    return redirect('empleado_index')