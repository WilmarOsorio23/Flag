import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from Modulo.forms import ModuloForm
from Modulo.models import Consultores, Empleado, Modulo

def modulo(request):
    # Ordenar los módulos por el campo 'id' en orden ascendente
    lista_modulos  = Modulo.objects.all().order_by('ModuloId')
    return render(request, 'Modulo/index.html', {'Modulo': lista_modulos})

    
def crear(request):
    if request.method == 'POST':
        form = ModuloForm(request.POST)
        if form.is_valid():
            max_id = Modulo.objects.all().aggregate(max_id=models.Max('ModuloId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_modulo = form.save(commit=False)
            nuevo_modulo.id = new_id
            nuevo_modulo.save()
            
            return redirect('Modulo')
    else:
        form = ModuloForm()
    return render(request, 'Modulo/crear.html', {'form': form})

@csrf_exempt
def editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            modulo = get_object_or_404(Modulo, pk=id)
            modulo.Modulo = data.get('Modulo', modulo.Modulo)  # Actualiza solo si está presente
            modulo.save()
            return JsonResponse({'status': 'success'})
        except Modulo.DoesNotExist:
            return JsonResponse({'status': 'error', 'errors': ['Módulo no encontrado']})
        except ValueError as ve:
            return JsonResponse({'status': 'error', 'errors': ['Error al procesar los datos: ' + str(ve)]})
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': ['Error desconocido: ' + str(e)]})
    return JsonResponse({'status': 'error', 'error': 'Método no permitido'})
    
def eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Modulo.objects.filter(ModuloId__in=item_ids).delete()
        return redirect('Modulo')
    return redirect('Modulo')

def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Empleado.objects.filter(ModuloId=id).exists() or
                Consultores.objects.filter(ModuloId=id).exists()
            ): 
                relacionados.append(id)

        if relacionados:
            return JsonResponse({
                'isRelated': True,
                'ids': relacionados
            })
        else:
            return JsonResponse({'isRelated': False})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def descargar_excel(request):
    # Verifica si la solicitud es POST
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete')  # Asegúrate de que este es el nombre correcto del campo
        # Convierte la cadena de IDs en una lista de enteros
    
        item_ids = list(map(int, item_ids.split (',')))  # Cambiado aquí
        modulos = Modulo.objects.filter(ModuloId__in=item_ids)

        # Crea una respuesta HTTP con el tipo de contenido de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Modulos.xlsx"'

        data = []
        for modulo in modulos:
            data.append([modulo.ModuloId, modulo.Modulo])

        df = pd.DataFrame(data, columns=['Id', 'Nombre'])
        df.to_excel(response, index=False)

        return response

    return redirect('Modulo')
