# Vista perfil
import json
from pyexpat.errors import messages
from turtle import pd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from Modulo import models
from Modulo.forms import PerfilForm
from Modulo.models import Consultores, Empleado, Nomina, Perfil
from django.db import models
import pandas as pd
from django.contrib import messages
def perfil_index(request):
    perfil_data = Perfil.objects.all()
    return render(request, 'perfil/perfil_index.html', {'perfil_data': perfil_data})


def perfil_crear(request):
     if request.method == 'POST':
        form = PerfilForm(request.POST)
        if form.is_valid():
            nuevo_perfil = form.save(commit=False)
            nuevo_perfil.save()  # Guardar directamente el registro con el Documento proporcionado
            return redirect('nomina_index')
     else:
        form = PerfilForm()
     return render(request, 'Nomina/nomina_form.html', {'form': form})

def perfil_editar(request,id):
     print("llego hasta views")
     if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            perfil = Perfil.objects.get(pk=id)
            form = PerfilForm(data, instance=perfil)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Perfil.DoesNotExist:
            return JsonResponse({'error': 'Módulo no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
     else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
     
     
def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Empleado.objects.filter(PerilId=id).exists() or
                Consultores.objects.filter(PerilId=id).exists()
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


def perfil_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Perfil.objects.filter(PerfilId__in=item_ids).delete()
        messages.success(request, 'Los perfiles seleccionados se han eliminado correctamente.')
        return redirect('perfil_index')
    return redirect('perfil_index')




# Vista para descargar Perfiles seleccionados en formato Excel
def perfil_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        perfil_data = []
        for item_id in item_ids:
            try:
                perfil = Perfil.objects.get(pk=item_id)
                perfil_data.append([
                    perfil.PerfilId,
                    perfil.Perfil 
                ])
            except Perfil.DoesNotExist:
                print(f"Perfil con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not perfil_data:
            return HttpResponse("No se encontraron registros de nómina.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(perfil_data, columns=['Id','perfil'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="perfil.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response

    return redirect('perfil_index') 
