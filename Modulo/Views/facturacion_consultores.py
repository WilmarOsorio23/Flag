from django.shortcuts import render
from Modulo.models import Facturacion_Consultores, Tiempos_Cliente, Tarifa_Consultores,Consultores,Linea,Clientes,Modulo
from Modulo.forms import FacturacionConsultoresFilterForm
from decimal import Decimal
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.shortcuts import redirect


def filtrar_facturacion_consultores(form, facturacion_consultores):
    anio = form.cleaned_data.get('Anio')
    mes_factura  = form.cleaned_data.get('Mes')
    mes_cobro = form.cleaned_data.get('Mes_Cobro')
    consultor = form.cleaned_data.get('Consultor')
    linea = form.cleaned_data.get('LineaId')
    

    if anio:
        facturacion_consultores = facturacion_consultores.filter(Anio=anio)
    if mes_factura :
        facturacion_consultores = facturacion_consultores.filter(Mes=mes_factura )
    if mes_cobro:
        facturacion_consultores = facturacion_consultores.filter(Periodo_Cobrado=mes_cobro)
    if consultor:
        facturacion_consultores = facturacion_consultores.filter(Documento=consultor)
    if linea:
        facturacion_consultores = facturacion_consultores.filter(LineaId=linea)

    return facturacion_consultores


def facturacion_consultores(request):
    facturacion_info = []
    totales_facturacion = {}
    facturacion_consultores = Facturacion_Consultores.objects.all()
    mensaje = ""
    page_size = 100  # Puedes ajustar este valor según lo que consideres óptimo
    page = int(request.GET.get('page', 1))

    if request.method == 'GET':
        form = FacturacionConsultoresFilterForm(request.GET)

        if form.is_valid():
            # Solo buscar si hay al menos un filtro principal aplicado
            filtros = [
                form.cleaned_data.get('Anio'),
                form.cleaned_data.get('Mes'),
                form.cleaned_data.get('Mes_Cobro'),
                form.cleaned_data.get('Consultor'),
                form.cleaned_data.get('LineaId'),
            ]
            if any(filtros):
                facturacion_consultores = filtrar_facturacion_consultores(form, facturacion_consultores)
                total_registros = facturacion_consultores.count()
                facturacion_consultores = facturacion_consultores[(page-1)*page_size:page*page_size]
                if facturacion_consultores.exists():
                    for registro in facturacion_consultores:        
                        facturacion_info.append({
                        'id': registro.id,  # <-- ESTE ES FUNDAMENTAL
                        'Anio': registro.Anio,
                        'Mes': registro.Mes,
                        'Consultor': registro.Documento.Nombre,  # Nombre del consultor
                        'ConsultorId': registro.Documento.Documento,
                        'Linea': registro.LineaId.Linea,  # Nombre de la línea
                        'LineaId': registro.LineaId.LineaId,
                        'Numero_Factura': registro.Cta_Cobro,  # Número de factura
                        'Periodo_Cobrado': registro.Periodo_Cobrado,  # Periodo cobrado
                        'Aprobado_Por': registro.Aprobado_Por,  # Aprobado por
                        'Fecha_Cobro': registro.Fecha_Cobro,  # Fecha de cobro
                        'Fecha_Pago': registro.Fecha_Pago,  # Fecha de pago
                        'Cliente': registro.ClienteId.Nombre_Cliente,  # Nombre del cliente
                        'ClienteId': registro.ClienteId.ClienteId,
                        'Modulo': registro.ModuloId.Modulo,  # Nombre del módulo
                        'ModuloId': registro.ModuloId.ModuloId,
                        'Cantidad_Horas': registro.Horas,  # Cantidad de horas
                        'Valor_Unitario': registro.Valor_Unitario,  # Valor unitario
                        'IVA': registro.IVA,  # IVA
                        'Valor_Neto': registro.Valor_Neto,  # Valor neto
                        'Retencion_Fuente': registro.Retencion_Fuente,  # Retención de fuente
                        'Valor_Pagado': registro.Valor_Pagado,  # Valor pagado
                        'Valor_Cobro': registro.Valor_Cobro,  # Valor cobrado
                        'Factura': registro.Factura,  # Factura asociada
                        'Valor_Factura_Cliente': registro.Valor_Fcta_Cliente,  # Valor de la factura para el cliente
                        'Fecha': registro.Fecha,  # Fecha de la factura
                        'Deuda_Tecnica': registro.Deuda_Tecnica,  # Deuda técnica
                        'Factura_Pendiente': registro.Factura_Pendiente,  # Factura pendiente
                        'Porcentaje_Dif': registro.Dif,
                        'Diferencia_Bruta': registro.Diferencia_Bruta,
                        'Observaciones': registro.Observaciones,  # Observaciones
                    })
                # Si no hay registros en facturacion_consultores, buscar en tiempos_clientes y tarifa_consultores
                if not facturacion_consultores.exists():
                    anio = form.cleaned_data['Anio']
                    mes_factura = form.cleaned_data['Mes']
                    mes_cobro = form.cleaned_data['Mes_Cobro']
                    consultor = form.cleaned_data['Consultor']
                    linea = form.cleaned_data['LineaId']

                    # Si no hay consultor, trae todos
                    if consultor:
                        if isinstance(consultor, str):
                            consultor_obj = Consultores.objects.filter(Documento=consultor).first()
                            consultores = [consultor_obj] if consultor_obj else []
                        else:
                            consultores = [consultor]
                    else:
                        consultores = Consultores.objects.all()
                    # Si no hay línea, trae todas
                    if linea:
                        if isinstance(linea, str):
                            linea_obj = Linea.objects.filter(LineaId=linea).first()
                            lineas = [linea_obj] if linea_obj else []
                        else:
                            lineas = [linea]
                    else:
                        lineas = Linea.objects.all()

                    for cons in consultores:
                        if cons is None:
                            continue
                        documento_consultor = cons.Documento
                        for lin in lineas:
                            if lin is None:
                                continue
                            nombre_linea = lin.Linea
                            linea_id = lin.LineaId  # 🔴 Obtener el ID de la línea

                            tiempos_clientes = Tiempos_Cliente.objects.filter(Anio=anio, Mes=mes_cobro, Documento=documento_consultor, LineaId=linea_id)
                            mes_str = str(mes_cobro).zfill(2)
                            tarifa_consultores = Tarifa_Consultores.objects.filter(anio=anio, mes=mes_str, documentoId=documento_consultor)
                            periodo_cobrado_real = mes_cobro  # Por defecto, el que viene en el filtro

                            # Si no hay tarifa para ese mes, buscar la más reciente anterior
                            if not tarifa_consultores.exists():
                                tarifa_anteriores = (
                                    Tarifa_Consultores.objects
                                    .filter(anio=anio, documentoId=documento_consultor, mes__lt=mes_str)
                                    .order_by('-mes')  # Mes más reciente anterior
                                )
                                tarifa_usada = tarifa_anteriores.first()
                                if tarifa_usada:
                                    periodo_cobrado_real = int(tarifa_usada.mes)
                                    tarifa_consultores = Tarifa_Consultores.objects.filter(
                                        anio=anio,
                                        mes=tarifa_usada.mes,
                                        documentoId=documento_consultor
                                    )
                            else:
                                tarifa_usada = tarifa_consultores.first()
                                if tarifa_usada:
                                    periodo_cobrado_real = int(tarifa_usada.mes)

                            # Calcular los valores pero sin insertar en la base de datos
                            for tiempo in tiempos_clientes:
                                tarifa = tarifa_consultores.filter(clienteID=tiempo.ClienteId).first()

                                if tarifa:
                                    valor_hora = Decimal(tarifa.valorHora or 0)
                                    horas = Decimal(tiempo.Horas or 0)
                                    valor_cobro = round(valor_hora * horas,2 or 0)
                                    porcentaje_iva = Decimal(tarifa.iva or 0) / 100
                                    porcentaje_retencion = Decimal(tarifa.rteFte or 0) / 100
                                    iva = round(porcentaje_iva * valor_cobro,2)
                                    retencion = round(porcentaje_retencion * valor_cobro,2)
                                    valor_neto = round(valor_cobro + iva,2)
                                    valor_pagado = round(valor_neto - retencion,2)

                                    # Aquí ya no guardamos en Facturacion_Consultores, solo calculamos y visualizamos
                                    facturacion_info.append({
                                        'id': id,  # <-- ESTE ES FUNDAMENTAL
                                        'Anio': anio,
                                        'Mes': mes_factura,
                                        'Consultor': cons.Nombre,
                                        'ConsultorId': cons.Documento,      # 🔥 Este es el valor que necesitas para el POST
                                        'Linea': nombre_linea,
                                        'LineaId': lin.LineaId,
                                        'Numero_Factura': None,
                                        'Periodo_Cobrado': mes_cobro,
                                        'Aprobado_Por': None,  # Aquí puedes poner lo que desees
                                        'Fecha_Cobro': None,
                                        'Fecha_Pago': None,
                                        'Cliente': tiempo.ClienteId.Nombre_Cliente,
                                        'ClienteId': tiempo.ClienteId.ClienteId,      # 🔥 Este es el valor que necesitas para el POST
                                        'Modulo': tiempo.ModuloId.Modulo,
                                        'ModuloId': tiempo.ModuloId.ModuloId,      # 🔥 Este es el valor que necesitas para el POST
                                        'Cantidad_Horas': tiempo.Horas,
                                        'Valor_Unitario': valor_hora,
                                        'Valor_Cobro': valor_cobro,
                                        'IVA': iva,
                                        'Valor_Neto': valor_neto,
                                        'Retencion_Fuente': retencion,
                                        'Valor_Pagado': valor_pagado,
                                        'Factura': None,  # Aquí puedes poner lo que desees
                                        'Valor_Factura_Cliente': None,
                                        'Fecha': None,
                                        'Deuda_Tecnica': None,
                                        'Factura_Pendiente': None,
                                        'Porcentaje_Dif': None,
                                        'Diferencia_Bruta': None,
                                        'Observaciones': None
                                    })

                # Recalcular totales
                totales_facturacion = {
                    'Total Valor Cobro': sum([row['Valor_Cobro'] for row in facturacion_info]),
                    'Total IVA': sum([row['IVA'] for row in facturacion_info]),
                    'Total Valor Pagado': sum([row['Valor_Pagado'] for row in facturacion_info]),
                }
                # Paginación
                total_paginas = (total_registros + page_size - 1) // page_size
            else:
                mensaje = "Por favor, aplica al menos un filtro para mostrar resultados."
                total_paginas = 0
                total_registros = 0
        else:
            mensaje = "Por favor, corrige los errores en el formulario."
            total_paginas = 0
            total_registros = 0
    else:
        form = FacturacionConsultoresFilterForm()
        total_paginas = 0
        total_registros = 0

    context = {
        'form': form,
        'facturacion_info': facturacion_info,
        'TotalesFacturacion': totales_facturacion,
        'mensaje': mensaje,
        'total_paginas': total_paginas,
        'pagina_actual': page,
        'total_registros': total_registros,
    }

    return render(request, 'Facturacion_Consultores/facturacion_consultores_index.html', context)

def safe_decimal(value):
    try:
        if value in [None, '', 'None']:
            return Decimal('0')
        return Decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal('0')

@csrf_exempt
def guardar_facturacion_consultores(request):
    if request.method == 'POST':
        try:
            indices = [
                key.split('_')[1] for key in request.POST.keys() if key.startswith('factura_')
            ]
            indices = list(set(indices))  # Evitar duplicados

            for i in indices:
                row_id = request.POST.get(f'factura_{i}')

                # Obtener o crear instancia
                if row_id == 'new':
                    row = Facturacion_Consultores()
                else:
                    row = Facturacion_Consultores.objects.filter(id=row_id).first() or Facturacion_Consultores()
                    
                # Campos comunes
                row.Anio = request.POST.get(f'Anio_{i}') or ''
                row.Mes = request.POST.get(f'Mes_{i}') or ''
                row.Documento = Consultores.objects.get(Documento=request.POST.get(f'ConsultorId_{i}'))
                row.ClienteId = Clientes.objects.get(ClienteId=request.POST.get(f'ClienteId_{i}'))
                row.ModuloId = Modulo.objects.get(ModuloId=request.POST.get(f'ModuloId_{i}'))
                row.LineaId = Linea.objects.get(LineaId=request.POST.get(f'LineaId_{i}'))
                row.Cta_Cobro = request.POST.get(f'Numero_Factura_{i}') or ''
                row.Aprobado_Por = request.POST.get(f'Aprobado_Por_{i}') or ''
                row.Fecha_Cobro = request.POST.get(f'Fecha_Cobro_{i}') or date.today()
                row.Fecha_Pago = request.POST.get(f'Fecha_Pago_{i}') or date.today()
                row.Periodo_Cobrado = request.POST.get(f'Periodo_Cobrado_{i}') or ''
                row.Factura = request.POST.get(f'Factura_{i}') or ''
                row.Fecha = request.POST.get(f'Fecha_{i}') or None
                row.Deuda_Tecnica = request.POST.get(f'Deuda_Tecnica_{i}') or ''
                row.Factura_Pendiente = request.POST.get(f'Factura_Pendiente_{i}') or ''
                row.Observaciones = request.POST.get(f'Observaciones_{i}') or ''

                # Campos decimales protegidos
                row.Horas = safe_decimal(request.POST.get(f'Cantidad_Horas_{i}'))
                row.Valor_Unitario = safe_decimal(request.POST.get(f'Valor_Unitario_{i}'))
                row.IVA = safe_decimal(request.POST.get(f'IVA_{i}'))
                row.Retencion_Fuente = safe_decimal(request.POST.get(f'Retencion_Fuente_{i}'))
                row.Valor_Cobro = safe_decimal(request.POST.get(f'Valor_Cobro_{i}'))
                row.Valor_Neto = safe_decimal(request.POST.get(f'Valor_Neto_{i}'))
                row.Valor_Pagado = safe_decimal(request.POST.get(f'Valor_Pagado_{i}'))
                row.Valor_Fcta_Cliente = safe_decimal(request.POST.get(f'Valor_Factura_Cliente_{i}'))

                # Cálculos
                valor_cliente = row.Valor_Fcta_Cliente
                valor_cobro = row.Valor_Cobro
                if valor_cliente  == 0:
                    diferencia_bruta = Decimal('0')
                    porcentaje_dif = Decimal('0')
                else:
                    diferencia_bruta = valor_cliente - valor_cobro
                    porcentaje_dif = abs(diferencia_bruta / valor_cliente) * 100

                row.Diferencia_Bruta = diferencia_bruta
                row.Dif = porcentaje_dif

                row.save()

            return redirect('facturacion_consultores_index')

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def eliminar_facturacion_consultores(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])
            if not ids:
                raise ValueError("No se proporcionaron IDs para eliminar.")
            Facturacion_Consultores.objects.filter(id__in=ids).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)
