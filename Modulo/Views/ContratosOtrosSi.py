#Contratos Otros Si
import json
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from django.db import models
from django.contrib import messages
from Modulo.forms import ContratosOtrosSiForm, ClientesContratos
from Modulo.models import ContratosOtrosSi
from django.db import IntegrityError


def contratos_otros_si_index(request):
    contratos_otros_si_data = ContratosOtrosSi.objects.all()
    form=ContratosOtrosSiForm()
    return render(request, 'contratos_otros_si/contratos_otros_si_index.html', {'contratos_otros_si_data': contratos_otros_si_data, 'form': form})

def contratos_otros_si_crear(request):
    if request.method == 'POST':
        form = ContratosOtrosSiForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contratos_otros_si_index')
    else:
        form = ContratosOtrosSiForm()
    return render(request, 'contratos_otros_si/contratos_otros_si_form.html', {'form': form})

def contratos_otros_si_editar(request, id):
    logger = logging.getLogger(__name__)
    logger.info("llego hasta editar")
    if request.method == 'POST':
        try:
            # Decodificar los datos JSON recibidos
            data = json.loads(request.body)
            
            # Obtener el contrato a editar
            contrato = get_object_or_404(ContratosOtrosSi, pk=id)
            
            # Actualizar los campos del contrato
            contrato.FechaFin = data.get('FechaFin', contrato.FechaFin)
            contrato.NumeroOtroSi = data.get('NumeroOtroSi', contrato.NumeroOtroSi)
            contrato.ValorOtroSi = data.get('ValorOtroSi', contrato.ValorOtroSi) or None
            contrato.ValorIncluyeIva = data.get('ValorIncluyeIva', contrato.ValorIncluyeIva)
            contrato.Polizas = data.get('Polizas', contrato.Polizas)
            contrato.PolizasDesc = data.get('PolizasDesc', contrato.PolizasDesc) or None
            contrato.FirmadoFlag = data.get('FirmadoFlag', contrato.FirmadoFlag)
            contrato.FirmadoCliente = data.get('FirmadoCliente', contrato.FirmadoCliente)
            contrato.Contrato = data.get('Contrato', contrato.Contrato)


            # Validar y asignar monedaId
            moneda_id = data.get('monedaId')
            if moneda_id:
                contrato.monedaId_id = moneda_id
            
            # Guardar los cambios en la base de datos
            contrato.save()
            # Retornar una respuesta exitosa
            return JsonResponse({'status': 'success'})
        except IntegrityError as e:
            if "FOREIGN KEY" in str(e):
                return JsonResponse({'error': 'No existe un contrato válido para la fecha de inicio seleccionada.'}, status=400)
            return JsonResponse({'error': 'Error de integridad: ' + str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos JSON'}, status=400)
        except Exception as e:
            # Capturar cualquier excepción y retornar un mensaje de error
            return JsonResponse({'error': str(e)}, status=500)
            '''
            # Retornar una respuesta exitosa
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos JSON'}, status=400)
        except Exception as e:
            # Capturar cualquier excepción y retornar un mensaje de error
            return JsonResponse({'error': str(e)}, status=500)
    contratos_cliente = ClientesContratos.objects.filter(ClienteId=contrato.ClienteId)
    form = ContratosOtrosSiForm(instance=contrato, cliente_id=contrato.ClienteId_id)
    return render(request, 'contratos_otros_si/contratos_otros_si_form.html', {
        'form': form,
        'contratos_cliente': contratos_cliente,
    })
    return JsonResponse({'error': 'Método no permitido'}, status=405)
'''
def contratos_otros_si_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        ContratosOtrosSi.objects.filter(ContratosOtrosSiId__in=item_ids).delete()
        messages.success(request, 'Los contratos seleccionados se han eliminado correctamente.')
    return redirect('contratos_otros_si_index')

def contratos_otros_si_descargar_excel(request):
    if request.method == 'POST':
        contratosotrossi_ids = request.POST.get('items_to_download')
        contratosotrossi_ids = list(map(int, contratosotrossi_ids.split(',')))
        contratosotrossi = ContratosOtrosSi.objects.filter(ContratosOtrosSiId__in=contratosotrossi_ids)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Contratos_Otros_Si.xlsx"'

        data = []
        for contratosotrosi in contratosotrossi:
            data.append([contratosotrosi.ContratosOtrosSiId,
                         contratosotrosi.ClienteId.Nombre_Cliente,
                         contratosotrosi.FechaInicio,
                         contratosotrosi.FechaFin,
                         contratosotrosi.NumeroOtroSi,
                         contratosotrosi.ValorOtroSi,
                         contratosotrosi.ValorIncluyeIva,
                         contratosotrosi.Polizas,
                         contratosotrosi.PolizasDesc,
                         contratosotrosi.FirmadoFlag,
                         contratosotrosi.FirmadoCliente,
                         contratosotrosi.monedaId.Nombre,
                         contratosotrosi.Contrato])
        df = pd.DataFrame(data, columns=['Id', 'Cliente', 'FechaInicio', 'FechaFin', 'NumeroOtroSi', 'ValorOtroSi',
                                         'ValorIncluyeIva', 'Polizas', 'PolizasDesc', 'FirmadoFlag', 'FirmadoCliente', 'Moneda', 'Contrato'])
        df.to_excel(response, index=False)
        return response
    return redirect('contratos_otros_si_index')
  