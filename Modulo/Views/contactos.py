import json
from urllib import request
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo.forms import ContactosForm
from Modulo.models import Contactos, Detalle_Gastos
from django.db import models
from django.contrib import messages

def contactos_index(request):
    contactos = Contactos.objects.all()
    return render(request, 'Contactos/contactos_index.html', {'contactos': contactos})  

def contactos_crear(request):
    if request.method == 'POST':
        form = ContactosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contactos_index')
    else:
        form = ContactosForm()
    return render(request, 'Contactos/contactos_form.html', {'form': form})         

def contactos_editar(request, id):
     print("llego hasta editar")
     if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalle = get_object_or_404( Contactos, pk=id)
            detalle.Nombre  = data.get('Nombre', detalle.Nombre)
            detalle.Telefono = data.get('Telefono', detalle.Telefono)
            detalle.Direccion = data.get('Direccion', detalle.Direccion)
            detalle.activo = data.get('Activo', detalle.activo)
            detalle.Cargo= data.get('Cargo', detalle.Cargo)
            detalle.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Contactos.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
     else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def contactos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Contactos.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
    return redirect('contactos_index')  

def contactos_descargar_excel(request):
     if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        detalles_data = []
        for item_id in item_ids:
            try:
                detalle = Contactos.objects.get(pk=item_id)
                detalles_data.append([
                    detalle.id,
                    detalle.clienteId.Nombre_Cliente,
                    detalle.contactoId.Descripcion  ,
                    detalle.Nombre,
                    detalle.Telefono,
                    detalle.Direccion,
                    detalle.CargoId.Cargo,
                    detalle.activo
                ])
            except Contactos.DoesNotExist:
                print(f"detalle con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not detalles_data:
            return HttpResponse("No se encontraron registros de detalles costos indirectos.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(detalles_data, columns=['Id','Cliente','Contacto','Nombre','Telefono','Direccion','Cargo','Activo'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Contactos.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
     
   
