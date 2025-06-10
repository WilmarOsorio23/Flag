import json
from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.contrib import messages
import pandas as pd
from django.http import HttpResponseBadRequest
from Modulo.models import ActividadPagare
from Modulo.forms import ActividadPagareForm

def actividad_pagare_index(request):
    actividades = ActividadPagare.objects.all()
    return render(request, 'Act_Maestro/Act_Maestro_index.html', {
        'actividades': actividades
    })

def actividad_pagare_crear(request):
    if request.method == 'POST':
        form = ActividadPagareForm(request.POST)
        if form.is_valid():
            try:
                actividad = form.save()
                print(f"Actividad creada: ID={actividad.Act_PagareId}, Código={actividad.Act_PagareId}, Descripción={actividad.Descripcion_Act}")
                messages.success(request, '¡Registro creado con éxito!')
                return redirect('actividad_pagare_index')
            except IntegrityError:
                messages.error(request, '¡El código ya existe!')
                return render(request, 'Act_Maestro/Act_Maestro_crear.html', {'form': form})
    else:
        form = ActividadPagareForm()
    
    return render(request, 'Act_Maestro/Act_Maestro_crear.html', {'form': form})
def actividad_pagare_editar(request, id):
    try:
        actividad = get_object_or_404(ActividadPagare, Act_PagareId=id)

        if request.method == 'POST':
            # Verifica si la solicitud es JSON (AJAX)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                actividad.Descripcion_Act = data.get('Descripcion_Act', actividad.Descripcion_Act)
                actividad.save()
                return JsonResponse({'status': 'success'})
            else:
                # Manejo de solicitudes POST tradicionales (formulario)
                form = ActividadPagareForm(request.POST, instance=actividad)
                if form.is_valid():
                    try:
                        form.save()
                        messages.success(request, '¡Cambios guardados!')
                        return redirect('actividad_pagare_index')
                    except IntegrityError:
                        messages.error(request, '¡El código ya existe!')
        
        # Si no es una solicitud POST, renderiza el formulario
        form = ActividadPagareForm(instance=actividad)
        return render(request, 'Act_Maestro/Act_Maestro_editar.html', {
            'form': form,
            'actividad': actividad
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def actividad_pagare_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete', '').split(',')

        print("IDs recibidos para eliminar:", item_ids)  # Depuración

        # Filtrar solo IDs válidos (números)
        try:
            item_ids = [int(id.strip()) for id in item_ids if id.strip().isdigit()]
        except ValueError:
            messages.error(request, "Los IDs enviados no son válidos.")
            return redirect('actividad_pagare_index')

        if not item_ids:
            messages.error(request, "No se seleccionaron actividades para eliminar.")
            return redirect('actividad_pagare_index')

        # Eliminar las actividades seleccionadas
        ActividadPagare.objects.filter(Act_PagareId__in=item_ids).delete()
        messages.success(request, "Actividades eliminadas correctamente.")
        return redirect('actividad_pagare_index')

    return HttpResponseBadRequest("Método no permitido")

def actividad_pagare_confirmar_delete(request, id):
    actividad = get_object_or_404(ActividadPagare, Act_PagareId=id)
    return render(request, 'Act_Maestro/Act_Maestro_confirmar_delete.html', {
        'actividad': actividad
    })

def actividad_pagare_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete', '').split(',')
        
        # Filtrar solo IDs válidos (números)
        item_ids = [int(id) for id in item_ids if id.strip().isdigit()]  # Elimina vacíos y convierte a enteros
        
        if not item_ids:
            messages.error(request, "No se seleccionaron actividades válidas para descargar.")
            return redirect('actividad_pagare_index')
        
        actividades = ActividadPagare.objects.filter(Act_PagareId__in=item_ids)
        
        # Crear DataFrame
        data = [[act.Act_PagareId, act.Descripcion_Act] for act in actividades]
        df = pd.DataFrame(data, columns=['ID Actividad', 'Descripción'])
        
        # Generar respuesta Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="actividades_pagare.xlsx"'
        df.to_excel(response, index=False)
        return response
    
    return redirect('actividad_pagare_index')