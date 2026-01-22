# Clientes Contratos
import json
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from modulo.forms import ClientesContratosForm
from modulo.models import ClientesContratos, ContratosOtrosSi
from django.db import models
from django.contrib import messages
from django.db import IntegrityError
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_clientes_contratos')
def clientes_contratos_index(request):
    clientes_contratos_data = ClientesContratos.objects.all()
    form = ClientesContratosForm()
    return render(request, 'ClientesContratos/ClientesContratosIndex.html', {'clientes_contratos_data': clientes_contratos_data, 'form': form})

@login_required
@verificar_permiso('can_manage_clientes_contratos')
def clientes_contratos_crear(request):
    if request.method == 'POST':
        form = ClientesContratosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes_contratos_index')
    else:
        form = ClientesContratosForm()
    return render(request, 'ClientesContratos/ClientesContratosForm.html', {'form': form})

@login_required
@verificar_permiso('can_manage_clientes_contratos')
def clientes_contratos_editar(request, id):
    logger = logging.getLogger(__name__)
    logger.info("llego hasta editar")
    if request.method == 'POST':
        try:
            # Decodificar los datos JSON recibidos
            data = json.loads(request.body)
            
            # Obtener el contrato a editar
            contrato = get_object_or_404(ClientesContratos, pk=id)

            # Validar el campo ContratoValor
            contrato_valor = data.get('ContratoValor')
            if contrato_valor:
                try:
                    contrato_valor = float(contrato_valor)
                    if contrato_valor > 99999999.99:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'El valor ingresado para ContratoValor excede el límite permitido (99,999,999.99).'
                        }, status=400)
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El valor ingresado para ContratoValor no es válido.'
                    }, status=400)
            
            # Actualizar los campos del contrato
            contrato.FechaFin = data.get('FechaFin', contrato.FechaFin)
            contrato.Contrato = data.get('Contrato', contrato.Contrato)
            contrato.ContratoVigente = data.get('ContratoVigente', contrato.ContratoVigente)
            contrato.OC_Facturar = data.get('OC_Facturar', contrato.OC_Facturar)
            contrato.Parafiscales = data.get('Parafiscales', contrato.Parafiscales)
            contrato.HorarioServicio = data.get('HorarioServicio', contrato.HorarioServicio)
            contrato.FechaFacturacion = data.get('FechaFacturacion', contrato.FechaFacturacion)
            contrato.TipoFacturacion = data.get('TipoFacturacion', contrato.TipoFacturacion)
            contrato.Observaciones = data.get('Observaciones', contrato.Observaciones)
            contrato.Polizas = data.get('Polizas', contrato.Polizas)
            contrato.PolizasDesc = data.get('PolizasDesc', contrato.PolizasDesc) or None
            contrato.ContratoValor = data.get('ContratoValor', contrato.ContratoValor) or None
            contrato.IncluyeIvaValor = data.get('IncluyeIvaValor', contrato.IncluyeIvaValor)
            contrato.ContratoDesc = data.get('ContratoDesc', contrato.ContratoDesc) or None
            contrato.ServicioRemoto = data.get('ServicioRemoto', contrato.ServicioRemoto)

            # Validar y asignar monedaId
            moneda_id = data.get('monedaId')
            if moneda_id:
                contrato.monedaId_id = moneda_id
            
            # Guardar los cambios en la base de datos
            contrato.save()
            
            # Retornar una respuesta exitosa
            return JsonResponse({'status': 'success'})
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos JSON'}, status=400)
        except Exception as e:
            # Capturar cualquier excepción y retornar un mensaje de error
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_clientes_contratos')
def clientes_contratos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')  # Obtener los IDs seleccionados desde el formulario

        try:
            item_ids = [int(id) for id in item_ids]  # Convertir los IDs a enteros
        except ValueError:
            messages.error(request, 'Error: Uno o más IDs no son válidos.')
            return redirect('clientes_contratos_index')

        # Verificar relaciones con la tabla ContratosOtrosSi
        relaciones = {}
        for id in item_ids:
            contrato = ClientesContratos.objects.get(pk=id)
            tablas_relacionadas = []

            # Verificar si el contrato está siendo usado en ContratosOtrosSi
            if ContratosOtrosSi.objects.filter(ClienteId=contrato.ClienteId, Contrato=contrato.Contrato).exists():
                tablas_relacionadas.append('Contratos Otros Sí')

            if tablas_relacionadas:
                relaciones[id] = tablas_relacionadas

        if relaciones:
            # Construir un mensaje detallado
            mensaje = "No se pueden eliminar los contratos seleccionados porque están relacionados con las siguientes tablas:<br>"
            for contrato_id, tablas in relaciones.items():
                mensaje += f"<strong>Contrato ID {contrato_id}:</strong> {', '.join(tablas)}<br>"
            messages.error(request, mensaje)
            return redirect('clientes_contratos_index')

        # Intentar eliminar los registros
        try:
            ClientesContratos.objects.filter(ClientesContratosId__in=item_ids).delete()
            messages.success(request, 'Clientes Contratos eliminados correctamente.')
        except IntegrityError:
            # Mensaje amigable para el usuario
            messages.error(
                request,
                "No se pueden eliminar los contratos seleccionados porque están relacionados con otras tablas, como 'Contratos Otros Sí'."
            )

        return redirect('clientes_contratos_index')
    return redirect('clientes_contratos_index')

@login_required
@verificar_permiso('can_manage_clientes_contratos')
def clientes_contratos_descargar_excel(request):
    if request.method == 'POST':
        clientescontratos_ids = request.POST.get('items_to_download')
        clientescontratos_ids = list(map(int, clientescontratos_ids.split(',')))
        clientescontratos = ClientesContratos.objects.filter(ClientesContratosId__in=clientescontratos_ids)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Clientes_Contactos.xlsx"'

        data = []
        for clientescontrato in clientescontratos:
            data.append([clientescontrato.ClientesContratosId,
                         clientescontrato.ClienteId.Nombre_Cliente,
                         clientescontrato.FechaInicio,
                         clientescontrato.FechaFin,
                         clientescontrato.Contrato,
                         clientescontrato.ContratoVigente,
                         clientescontrato.OC_Facturar,
                         clientescontrato.Parafiscales,
                         clientescontrato.HorarioServicio,
                         clientescontrato.FechaFacturacion,
                         clientescontrato.TipoFacturacion,
                         clientescontrato.Observaciones,
                         clientescontrato.Polizas,
                         clientescontrato.PolizasDesc,
                         clientescontrato.ContratoValor,
                         clientescontrato.IncluyeIvaValor,
                         clientescontrato.ContratoDesc,
                         clientescontrato.ServicioRemoto,
                         getattr(clientescontrato.monedaId, 'Nombre', 'Sin Moneda')])
        df = pd.DataFrame(data, columns=['Id', 'Cliente', 'FechaInicio', 'FechaFin', 'Contrato', 
                                         'ContratoVigente', 'OC_Facturar', 'Parafiscales', 'HorarioServicio', 'FechaFacturacion', 
                                         'TipoFacturacion', 'Observaciones', 'Polizas', 'PolizasDesc',  'ContratoValor',
                                         'IncluyeIvaValor', 'ContratoDesc', 'ServicioRemoto', 'Moneda'])
        df.to_excel(response, index=False)
        return response
    return redirect('clientes_contratos_index')

@login_required
@verificar_permiso('can_manage_clientes_contratos')
def verificar_relaciones_contratos(request):
    """
    Verifica si los contratos de clientes están relacionados con otros registros.

    Parámetros:
        - request: La solicitud HTTP.

    Métodos:
        - POST: Recibe una lista de IDs de contratos y verifica sus relaciones.

    Respuestas:
        - JsonResponse con detalles de las relaciones si existen.
        - JsonResponse con error si no se envían IDs o si ocurre un error.
    """
    if request.method == 'POST':
        try:
            # Cargar los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            ids = data.get('ids', [])

            # Verifica que los ids estén presentes y bien formados
            if not ids:
                return JsonResponse({'error': 'No se han enviado IDs'}, status=400)

            # Diccionario para almacenar los detalles de las relaciones
            relaciones = {}

            for id in ids:
                # Verifica si el contrato está relacionado con otros registros
                relaciones_contrato = []
                if ContratosOtrosSi.objects.filter(ClienteId=id).exists():
                    relaciones_contrato.append('ContratosOtrosSi')

                if relaciones_contrato:
                    relaciones[id] = relaciones_contrato

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