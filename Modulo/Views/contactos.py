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
            max_id = Contactos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_moneda = form.save(commit=False)
            nuevo_moneda.id = new_id
            nuevo_moneda.save()
        return redirect('contactos_index')
    else:
     form = ContactosForm()
     return render(request, 'Contactos/contactos_form.html', {'form': form})  # Se ajusta el redireccionamiento 

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
     
     # Verifica si la solicitud es POST
    if request.method == 'POST':
        contacto_ids = request.POST.get('items_to_download')  
        # Convierte la cadena de IDs en una lista de enteros
        contacto_ids = list(map(int, contacto_ids.split (','))) 
        contacto = Contactos.objects.filter(id__in=contacto_ids)
        # Crea una respuesta HTTP con el tipo de contenido de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Contactos.xlsx"'

        data = []
        for contactos in contacto:
            data.append([contactos.id,
                         contactos.clienteId.Nombre_Cliente,
                         contactos.contactoId.Descripcion, 
                         contactos.Nombre,
                         contactos.Telefono,
                         contactos.Direccion,
                         contactos.Cargo,
                        contactos.activo])

        df = pd.DataFrame(data, columns=['Id','Cliente','Contacto','Nombre','Telefono','Direccion','Cargo','Activo'])
        df.to_excel(response, index=False)

        return response

    return redirect('contactos_index')
     
   
