import json
from urllib import request
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo.forms import EmpleadosEstudiosForm
from Modulo.models import Empleados_Estudios
from django.db import models
from django.contrib import messages
from django.http import HttpResponse, JsonResponse

def empleados_estudios_index(request):
    empleados_estudios = Empleados_Estudios.objects.all()
    return render(request, 'Empleados_Estudios/Empleados_Estudios_index.html', {'empleados_estudios': empleados_estudios})

def empleados_estudios_crear(request):
    if request.method == 'POST':
        form = EmpleadosEstudiosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('empleados_estudios_index')
    else:
        form = EmpleadosEstudiosForm()
    return render(request, 'Empleados_Estudios/Empleados_Estudios_form.html', {'form': form})  

def empleados_estudios_editar(request, id):
   print("llego hasta editar")
   if request.method == 'POST':
        try:
            data = json.loads(request.body)
            estudios = get_object_or_404( Empleados_Estudios, pk=id)
            estudios.titulo = data.get('titulo', estudios.titulo)
            estudios.institucion = data.get('institucion', estudios.institucion)
            estudios.fecha_Inicio = data.get('fecha_Inicio', estudios.fecha_Inicio)
            estudios.fecha_Fin = data.get('fecha_Fin', estudios.fecha_Fin)
            estudios.fecha_Graduacion = data.get('fecha_Graduacion', estudios.fecha_Graduacion)
            estudios.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Empleados_Estudios.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
   else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def empleados_estudios_eliminar(request):
     if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Empleados_Estudios.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
     return redirect('empleados_estudios_index') 

def empleados_estudios_descargarExcel(request):
    if request.method == 'POST':
        empleadoestudio_ids = request.POST.get('items_to_download')
        empleadoestudio_ids = list(map(int, empleadoestudio_ids.split (','))) 
        empleadoestudio = Empleados_Estudios.objects.filter(id__in=empleadoestudio_ids)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Empleados_Estudios.xlsx"'

        data = []
        for empleadoestudios in empleadoestudio:
            data.append([
                empleadoestudios.id,
                empleadoestudios.documentoId.Documento,
                empleadoestudios.documentoId.Nombre,
                empleadoestudios.titulo,
                empleadoestudios.institucion,
                empleadoestudios.fecha_Inicio,
                empleadoestudios.fecha_Fin,
                empleadoestudios.fecha_Graduacion,
            ])
        df = pd.DataFrame(data, columns=['Id', 'documentoId', 'Nombre Empleado', 'Titulo', 'Institucion', 'FechaInicio', 'FechaFin', 'FechaGraduacion'])
        df.to_excel(response, index=False)
        return response
    return redirect('empleados_estudios_index')




