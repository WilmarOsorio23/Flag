# Clientes Contratos
import json
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo.forms import ClientesContratosForm
from Modulo.models import ClientesContratos
from django.db import models
from django.contrib import messages

def clientes_contratos_index(request):
    clientes_contratos_data = ClientesContratos.objects.all()
    return render(request, 'clientes_contratos/clientes_contratos_index.html', {'clientes_contratos_data': clientes_contratos_data})

def clientes_contratos_crear(request):
    if request.method == 'POST':
        form = ClientesContratosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes_contratos_index')
    else:
        form = ClientesContratosForm()
    return render(request, 'clientes_contratos/clientes_contratos_form.html', {'form': form})


def clientes_contratos_editar(request, id):
    logger = logging.getLogger(__name__)
    logger.info("llego hasta editar")
    if request.method == 'POST':
        try:
            # Decodificar los datos JSON recibidos
            data = json.loads(request.body)
            
            # Obtener el contrato a editar
            contrato = get_object_or_404(ClientesContratos, pk=id)
            
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
            #contrato.ContratoValor = data.get('ContratoValor', contrato.ContratoValor) or None
            contrato.IncluyeIvaValor = data.get('IncluyeIvaValor', contrato.IncluyeIvaValor)
            contrato.ContratoDesc = data.get('ContratoDesc', contrato.ContratoDesc) or None
            contrato.ServicioRemoto = data.get('ServicioRemoto', contrato.ServicioRemoto)
            
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

def clientes_contratos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        ClientesContratos.objects.filter(ClientesContratosId__in=item_ids).delete()
        messages.success(request, 'Los contratos seleccionados se han eliminado correctamente.')
    return redirect('clientes_contratos_index')

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
                         clientescontrato.IncluyeIvaValor,
                         clientescontrato.ContratoDesc,
                         clientescontrato.ServicioRemoto])
        df = pd.DataFrame(data, columns=['Id', 'Cliente', 'FechaInicio', 'FechaFin', 'Contrato', 
                                         'ContratoVigente', 'OC_Facturar', 'Parafiscales', 'HorarioServicio', 'FechaFacturacion', 
                                         'TipoFacturacion', 'Observaciones', 'Polizas', 'PolizasDesc',  
                                         'IncluyeIvaValor', 'ContratoDesc', 'ServicioRemoto'])
        df.to_excel(response, index=False)
        return response
    return redirect('clientes_contratos_index')
