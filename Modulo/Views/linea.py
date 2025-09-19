# Vista para linea
import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from Modulo.forms import LineaForm
from Modulo.models import Consultores, Empleado, Linea
from django.db import models
from django.contrib import messages
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_linea')

def linea_index(request):
    linea_data = Linea.objects.all()
    return render(request, 'Linea/linea_index.html', {'lineas': linea_data})

@login_required
@verificar_permiso('can_manage_linea')
def linea_crear(request):
    if request.method == 'POST':
        form = LineaForm(request.POST)
        if form.is_valid():
            max_id = Linea.objects.all().aggregate(max_id=models.Max('LineaId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nueva_linea = form.save(commit=False)
            nueva_linea.LineaId= new_id
            nueva_linea.save()
            return redirect('linea_index')
    else:
        form = LineaForm()
    return render(request, 'linea/linea_form.html', {'form': form})

@login_required
@verificar_permiso('can_manage_linea')
def linea_editar(request, id):
    print("llego hasta views")
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            linea = Linea.objects.get(pk=id)
            form = LineaForm(data, instance=linea)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Linea.DoesNotExist:
            return JsonResponse({'error': 'Linea no encontrada'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
@login_required
@verificar_permiso('can_manage_linea')
def verificar_relaciones(request):
    print('entro a verificar relaciones')
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids',[])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Empleado.objects.filter(LineaId=id).exists() or
                Consultores.objects.filter(LineaId=id).exists()
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

@login_required
@verificar_permiso('can_manage_linea')
def linea_eliminar(request):
     if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Linea.objects.filter(LineaId__in=item_ids).delete()
        messages.success(request, 'Los perfiles seleccionados se han eliminado correctamente.')
        return redirect('linea_index')
     return redirect('linea_index')

@login_required
@verificar_permiso('can_manage_linea')
def linea_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')  
        print(item_ids) 

       
        linea_data = Linea.objects.filter(LineaId__in=item_ids)

        # Verifica si existen datos seleccionados
        if not linea_data.exists():
            messages.error(request, "No se encontraron datos para descargar.")  # Aquí usas messages
            return redirect('linea_index')

        # Prepara los datos para exportar
        data = []
        for linea in linea_data:
            data.append([linea.LineaId, linea.Linea])

        # Crea un DataFrame con los datos obtenidos
        df = pd.DataFrame(data, columns=['id', 'Linea'])

        # Configura la respuesta HTTP para enviar el archivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Linea.xlsx"'

        # Escribe el DataFrame al archivo Excel
        df.to_excel(response, index=False)

        # Retorna el archivo al cliente para descargar
        return response

    # Redirige a la página principal si no es un método POST
    return redirect('linea_index')

