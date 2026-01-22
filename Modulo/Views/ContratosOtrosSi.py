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
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_contratos_otros_si')
def contratos_otros_si_index(request):
    contratos_otros_si_data = ContratosOtrosSi.objects.all()
    form=ContratosOtrosSiForm()
    return render(request, 'ContratosOtrosSi/ContratosOtrosSiIndex.html', {'contratos_otros_si_data': contratos_otros_si_data, 'form': form})

@login_required
@verificar_permiso('can_manage_contratos_otros_si')
def contratos_otros_si_crear(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('ClienteId')
        contrato_id = request.POST.get('Contrato')  # Obtener el ID del contrato seleccionado
        form = ContratosOtrosSiForm(request.POST, cliente_id=cliente_id)
        if form.is_valid():
            contrato_cliente = ClientesContratos.objects.filter(ClientesContratosId=contrato_id).first()
            if contrato_cliente:
                # Asignar el valor del campo Contrato al campo Contrato de ContratosOtrosSi
                contrato_otros_si = form.save(commit=False)
                contrato_otros_si.Contrato = contrato_cliente.Contrato
                contrato_otros_si.save()
                return redirect('contratos_otros_si_index')
    else:
        form = ContratosOtrosSiForm()
    return render(request, 'ContratosOtrosSi/ContratosOtrosSiCrear.html', {'form': form})

@login_required
@verificar_permiso('can_manage_contratos_otros_si')
def contratos_otros_si_editar(request, id):
    logger = logging.getLogger(__name__)
    logger.info("llego hasta editar")
    if request.method == 'POST':
        try:
            # Decodificar los datos JSON recibidos
            data = json.loads(request.body)

            numero_otro_si = data.get('NumeroOtroSi', '').strip()

            if not numero_otro_si:
                return JsonResponse({'error': 'El campo Número Otro Sí no puede estar vacío.'}, status=400)

            
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
    return render(request, 'Contratosotrossi/Contratosotrossiform.html', {
        'form': form,
        'contratos_cliente': contratos_cliente,
    })
    return JsonResponse({'error': 'Método no permitido'}, status=405)
'''
@login_required
@verificar_permiso('can_manage_contratos_otros_si')
def contratos_otros_si_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        ContratosOtrosSi.objects.filter(ContratosOtrosSiId__in=item_ids).delete()
        messages.success(request, 'Los contratos seleccionados se han eliminado correctamente.')
    return redirect('contratos_otros_si_index')

@login_required
@verificar_permiso('can_manage_contratos_otros_si')
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

@login_required
@verificar_permiso('can_manage_contratos_otros_si')
def obtener_contratos_por_cliente(request, cliente_id):
    #contratos = ClientesContratos.objects.filter(ClienteId=cliente_id, ContratoVigente=True)
    contratos = ClientesContratos.objects.filter(ClienteId=cliente_id)
    data = [
        {'id': contrato.ClientesContratosId, 'nombre': contrato.Contrato}
        for contrato in contratos
    ]
    return JsonResponse({'contratos': data})