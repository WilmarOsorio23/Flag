import json
from urllib import request
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from modulo.forms import ContactosForm
from modulo.models import Contactos, Detalle_Gastos
from django.db import models
from django.contrib import messages
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_contactos')
def contactos_index(request):
    contactos = Contactos.objects.all()
    return render(request, 'Contactos/ContactosIndex.html', {'contactos': contactos})  

@login_required
@verificar_permiso('can_manage_contactos')
def contactos_crear(request):
    if request.method == 'POST':
        form = ContactosForm(request.POST)
        if form.is_valid():
            max_id = Contactos.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_contacto = form.save(commit=False)
            nuevo_contacto.id = new_id
            nuevo_contacto.save()
        return redirect('contactos_index')
    else:
        form = ContactosForm()
    return render(request, 'Contactos/ContactosForm.html', {'form': form}) 

@login_required
@verificar_permiso('can_manage_contactos')
def contactos_editar(request, id):
    print("Llego a editar")  # Confirmar que la función se está ejecutando
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)  # Depuración de los datos recibidos
            contacto = get_object_or_404(Contactos, pk=id)
            contacto.Nombre = data.get('Nombre', contacto.Nombre)
            contacto.Telefono = data.get('Telefono', contacto.Telefono)
            contacto.telefono_fijo = data.get('Telefono_Fijo', contacto.telefono_fijo)  # Nuevo campo
            contacto.correo = data.get('Correo', contacto.correo)  # Nuevo campo
            contacto.Direccion = data.get('Direccion', contacto.Direccion)
            contacto.activo = data.get('Activo', contacto.activo)
            contacto.Cargo = data.get('Cargo', contacto.Cargo)
            contacto.save()
            print("Contacto actualizado correctamente.")  # Confirmar que se guardó
            return JsonResponse({'status': 'success'})
        except Contactos.DoesNotExist:
            print("Error: Contacto no encontrado.")  # Depuración
            return JsonResponse({'error': 'Contacto no encontrado'}, status=404)
        except json.JSONDecodeError:
            print("Error: Formato de datos inválido.")  # Depuración
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
        except Exception as e:
            print("Error inesperado:", str(e))  # Depuración
            return JsonResponse({'error': 'Error inesperado: ' + str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_contactos')
def contactos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Contactos.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
    return redirect('contactos_index')  

@login_required
@verificar_permiso('can_manage_contactos')
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
     
   
