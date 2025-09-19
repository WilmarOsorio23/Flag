# Vista para la tabla Clientes
import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import pandas as pd
from django.db.models import Q
from Modulo import models
from django.db import models
from Modulo.forms import ClientesForm
from Modulo.models import Clientes, Contactos, Tiempos_Cliente, TiemposFacturables, Tarifa_Clientes
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_clientes')
# Vista para listar todos los clientes
def clientes_index(request):
    clientes = Clientes.objects.all()
    contactos = Contactos.objects.all()
    contactos_por_cliente = {}
    for contacto in contactos:
        if contacto.clienteId_id not in contactos_por_cliente:
            contactos_por_cliente[contacto.clienteId_id] = []
        contactos_por_cliente[contacto.clienteId_id].append({'id': contacto.id, 'Nombre': contacto.Nombre})
    
    # Serializar contactos_por_cliente a JSON
    contactos_por_cliente_json = json.dumps(contactos_por_cliente)
    return render(request, 'clientes/clientes_index.html', {
        'clientes': clientes,
        'contactos_por_cliente': contactos_por_cliente_json
    })

@login_required
@verificar_permiso('can_manage_clientes')
# Vista para crear un nuevo cliente
def clientes_crear(request):
    if request.method == 'POST':
        form = ClientesForm(request.POST)
        if form.is_valid():
            max_id = Clientes.objects.all().aggregate(max_id=models.Max('ClienteId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_cliente = form.save(commit=False)
            nuevo_cliente.ClienteId = new_id
            nuevo_cliente.save()
            return redirect('clientes_index')
    else:
        form = ClientesForm()
    
    return render(request, 'clientes/clientes_form.html', {'form': form})

@login_required
@verificar_permiso('can_manage_clientes')
# Vista para editar un cliente existente
@csrf_exempt
def clientes_editar(request, id):
    """
    Edita un cliente existente.

    Parámetros:
        - request: La solicitud HTTP.
        - id: El ID del cliente a editar.

    Métodos:
        - POST: Actualiza los datos del cliente con los valores proporcionados en el cuerpo de la solicitud.

    Respuestas:
        - JsonResponse con estado 'success' si la actualización es exitosa.
        - JsonResponse con error 'Cliente no encontrado' si el cliente no existe.
        - JsonResponse con error 'Error en el formato de los datos' si hay un error en el formato JSON.
        - JsonResponse con error 'No se puede desactivar un cliente sin una fecha de retiro' si se intenta desactivar un cliente sin proporcionar una fecha de retiro.
        - JsonResponse con error 'Método no permitido' si el método HTTP no es POST.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente = get_object_or_404( Clientes, pk=id)

            # Actualizar los campos del cliente con los datos recibidos
            cliente.Nombre_Cliente = data.get('Nombre_Cliente', cliente.Nombre_Cliente)           
            cliente.Activo = data.get('Activo', cliente.Activo) == 'True'
            cliente.Fecha_Inicio= data.get('Fecha_Inicio', cliente.Fecha_Inicio)
            cliente.Fecha_Retiro = data.get('Fecha_Retiro', cliente.Fecha_Retiro) or None
            cliente.Direccion = data.get('Direccion', cliente.Direccion) or None
            cliente.Telefono = data.get('Telefono', cliente.Telefono) or None
            cliente.CorreoElectronico = data.get('CorreoElectronico', cliente.CorreoElectronico) or None
            cliente.BuzonFacturacion = data.get('BuzonFacturacion', cliente.BuzonFacturacion) or None
            cliente.TipoCliente = data.get('TipoCliente', cliente.TipoCliente) or None
            cliente.Ciudad = data.get('Ciudad', cliente.Ciudad) or None
            cliente.Departamento = data.get('Departamento', cliente.Departamento) or None
            cliente.Pais = data.get('Pais', cliente.Pais) or None
            cliente.Nacional = data.get('Nacional', cliente.Nacional) == 'True'
            cliente.ContactoID_id = data.get('ContactoID', cliente.ContactoID_id) or None

            # Validación adicional: Si Activo es False y no hay Fecha_Retiro, no permitir guardar
            if not cliente.Activo and not cliente.Fecha_Retiro:
                return JsonResponse({'error': 'No se puede desactivar un cliente sin una fecha de retiro.'}, status=400)

            cliente.full_clean()
            cliente.save()

            return JsonResponse({'status': 'success'})
        except Clientes.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_clientes')
# Vista para eliminar clientes seleccionados
def clientes_eliminar(request):
    """
    Elimina clientes seleccionados.

    Parámetros:
        - request: La solicitud HTTP.

    Métodos:
        - POST: Elimina los clientes cuyos IDs se proporcionan en la solicitud.

    Respuestas:
        - Redirige a 'clientes_index' después de eliminar los clientes seleccionados.
        - Muestra mensajes de éxito o error según corresponda.
    """
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')  # Obtener los IDs seleccionados desde el formulario

        # Verificar si los IDs son válidos y convertirlos a enteros
        try:
            item_ids = [int(id) for id in item_ids]  # Convertir los IDs a enteros, si no lo son
        except ValueError:
            messages.error(request, 'Error: Uno o más IDs no son válidos.')
            return redirect('clientes_index')

        # Verificar que los clientes existen antes de eliminar
        clientes_a_eliminar = Clientes.objects.filter(ClienteId__in=item_ids)
        if clientes_a_eliminar.exists():
            clientes_a_eliminar.delete()
            messages.success(request, 'Los Clientes seleccionados se han eliminado correctamente.')
        else:
            messages.error(request, 'Error: No se encontraron clientes con los IDs seleccionados.')#ENTRA AQUI

        return redirect('clientes_index')  # Redirigir después de la eliminación

    return redirect('clientes_index')  # Redirigir si el método no es POST

@login_required
@verificar_permiso('can_manage_clientes')
# Vista para verificar relaciones de clientes con otros registros
def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        # Cargar los datos del cuerpo de la solicitud
        data = json.loads(request.body)
        ids = data.get('ids', [])
        try:
            
            # Verifica que los ids estén presentes y bien formados
            if not ids:
                return JsonResponse({'error': 'No se han enviado IDs'}, status=400)

            # Diccionario para almacenar los detalles de las relaciones
            relaciones = {}

            for id in ids:
                # Verifica si el cliente está relacionado con otros registros
                relaciones_cliente = []
                if Contactos.objects.filter(clienteId=id).exists():
                    relaciones_cliente.append('Contactos')
                if Tiempos_Cliente.objects.filter(ClienteId=id).exists():
                    relaciones_cliente.append('Tiempos_Cliente')
                if TiemposFacturables.objects.filter(ClienteId=id).exists():
                    relaciones_cliente.append('TiemposFacturables')
                if Tarifa_Clientes.objects.filter(clienteId=id).exists():
                    relaciones_cliente.append('Tarifa_Clientes')

                if relaciones_cliente:
                    relaciones[id] = relaciones_cliente

            # Responde con los detalles de las relaciones
            if relaciones:
                return JsonResponse({
                    'isRelated': True,
                    'relaciones': relaciones
                })
            else:
                return JsonResponse({'isRelated': False})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error en servidor: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_clientes')
def clientes_descargar_excel(request):
    """
    Descarga los clientes seleccionados en un archivo Excel.

    Parámetros:
        - request: La solicitud HTTP.

    Métodos:
        - POST: Genera un archivo Excel con los clientes cuyos IDs se proporcionan en la solicitud.

    Respuestas:
        - HttpResponse con el archivo Excel si la descarga es exitosa.
        - Redirige a 'clientes_index' con un mensaje de error si no se encontraron datos para descargar.
    """
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete', '')
        item_ids = item_ids.split(',')
        item_ids = [int(item) for item in item_ids]
        clientes = Clientes.objects.filter(ClienteId__in=item_ids)
        
        # Verificar si se recibieron IDs
        if not clientes.exists():
            messages.error(request, "No se encontraron datos para descargar.")
            return redirect('clientes_index')
        
        # Consultar las nóminas usando las IDs
        data = []
        for cliente in clientes:
            contacto_nombre = cliente.ContactoID.Nombre if cliente.ContactoID else ''
            data.append([
                cliente.ClienteId,
                cliente.Nombre_Cliente,
                cliente.Activo,
                cliente.Fecha_Inicio,
                cliente.Fecha_Retiro,
                cliente.Direccion,
                cliente.Telefono,
                cliente.CorreoElectronico,
                contacto_nombre,
                cliente.BuzonFacturacion,
                cliente.TipoCliente,
                cliente.Ciudad,
                cliente.Departamento,
                cliente.Pais,
                cliente.Nacional                   
            ])
        
        # Crear DataFrame de pandas
        df = pd.DataFrame(data, columns=['ClienteID', 'Nombre', 'Activo', 'Fecha de Inicio', 'Fecha de Retiro',
                                         'Direccion', 'Telefono', 'Correo Electronico','Contacto Principal', 'Buzon de Facturacion', 'Tipo de Cliente',
                                         'Ciudad', 'Departamento', 'Pais', 'Nacional'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Clientes.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response
    return redirect('clientes_index')

@login_required
@verificar_permiso('can_manage_clientes')
# Nueva vista para obtener los contactos de un cliente
def obtener_contactos(request):
    """
    Obtiene los contactos de un cliente específico.

    Parámetros:
        - request: La solicitud HTTP.

    Métodos:
        - GET: Devuelve una lista de contactos para el cliente especificado.

    Respuestas:
        - JsonResponse con la lista de contactos si el cliente existe.
        - JsonResponse con error 'Cliente no encontrado' si el cliente no existe.
    """
    cliente_id = request.GET.get('clienteId')
    if cliente_id:
        contactos = Contactos.objects.filter(clienteId=cliente_id).values('id', 'Nombre')
        return JsonResponse(list(contactos), safe=False)
    return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
