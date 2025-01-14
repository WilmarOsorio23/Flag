# Tipos de Contactos
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo.forms import TiposContactosForm
from Modulo.models import Contactos, TiposContactos
from django.db import models
from django.contrib import messages

def Tipos_contactos_index(request):
    tipos_contactos_data = TiposContactos.objects.all()
    return render(request, 'Tipos_Contactos/Tipos_Contactos_index.html', {'tipos_contactos_data': tipos_contactos_data})  

def Tipos_contactos_crear(request):
    if request.method == 'POST':
        form = TiposContactosForm(request.POST)
        if form.is_valid():
            max_id = TiposContactos.objects.all().aggregate(max_id=models.Max('contactoId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_contacto = form.save(commit=False)
            nuevo_contacto.contactoId = new_id  # Asignar un nuevo ID
            nuevo_contacto.save()
            return redirect('tipos_contactos_index')
    else:   
        form = TiposContactosForm()
    return render(request, 'Tipos_Contactos/Tipos_Contactos_form.html', {'form': form})

def Tipos_contactos_editar(request, id):    
   print("llego hasta editar")
   if request.method == 'POST':
        try:
            data = json.loads(request.body)
            contacto = get_object_or_404( TiposContactos, pk=id)
            contacto.Descripcion = data.get('Descripcion', contacto.Descripcion)
            contacto.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except TiposContactos.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
   else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def Tipos_contactos_eliminar(request):
  if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        TiposContactos.objects.filter(contactoId__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
  return redirect('tipos_contactos_index')


def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los tipos de contactos están relacionados
        relacionados = []
        for id in ids:
            if (
               Contactos.objects.filter(contactoId=id).exists()
                
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

def Tipos_contactos_descargar_excel(request):       
   if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                Contacto = TiposContactos.objects.get(pk=item_id)
                detalles_data.append([
                    Contacto.contactoId,
                    Contacto.Descripcion,
                   
                ])
            except TiposContactos.DoesNotExist:
                print(f"detalle con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not detalles_data:
            return HttpResponse("No se encontraron registros de detalles costos indirectos.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(detalles_data, columns=['Id','Descripcion'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Contactos.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
                                                        
