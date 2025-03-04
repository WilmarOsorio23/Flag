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
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                cargo = Empleados_Estudios.objects.get(pk=item_id)
                detalles_data.append([
                    cargo.id,
                    cargo.documentoId.Documento,
                    cargo.documentoId.Nombre,
                    cargo.fecha_Inicio,
                    cargo.fecha_Fin,
                ])
            except Empleados_Estudios.DoesNotExist:
                print(f"detalle con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not detalles_data:
            return HttpResponse("No se encontraron registros de detalles costos indirectos.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(detalles_data, columns=['Id','documentoId','Nombre Empleado','FechaInicio','FechaFin'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="EmpleadoEstudios.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
    return response




