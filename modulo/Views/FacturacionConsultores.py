from django.shortcuts import render
from modulo.models import Facturacion_Consultores, Tiempos_Cliente, Tarifa_Consultores, Consultores, Linea, Clientes, Modulo
from modulo.forms import FacturacionConsultoresFilterForm
from decimal import Decimal
from datetime import date
from decimal import Decimal, InvalidOperation

from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.shortcuts import redirect
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

# QUITAR LOS DECORADORES DE ESTA FUNCIÓN - No es una vista
def filtrar_tiempos_clientes(form):
    anio = form.cleaned_data.get('Anio')
    mes_cobro = form.cleaned_data.get('Mes_Cobro')
    consultor = form.cleaned_data.get('Consultor')
    linea = form.cleaned_data.get('LineaId')
    filtros = {}
    if anio:
        filtros['Anio'] = anio
    if mes_cobro:
        filtros['Mes'] = mes_cobro
    if consultor:
        filtros['Documento'] = consultor
    if linea:
        filtros['LineaId'] = linea
    return Tiempos_Cliente.objects.filter(**filtros)

def obtener_tarifa(anio, mes_cobro, documento, cliente_id):
    mes_str = str(mes_cobro).zfill(2)
    tarifa = Tarifa_Consultores.objects.filter(anio=anio, mes=mes_str, documentoId=documento, clienteID=cliente_id).first()
    if not tarifa:
        tarifa_anteriores = Tarifa_Consultores.objects.filter(anio=anio, documentoId=documento, clienteID=cliente_id, mes__lt=mes_str).order_by('-mes')
        tarifa = tarifa_anteriores.first()
    return tarifa

@login_required
@verificar_permiso('can_manage_facturacion_consultores')
def facturacion_consultores(request):
    facturacion_info = []
    totales_facturacion = {}
    mensaje = ""
    page_size = 50
    page = int(request.GET.get('page', 1))

    if request.method == 'GET':
        form = FacturacionConsultoresFilterForm(request.GET)
        if form.is_valid():
            filtros = [
                form.cleaned_data.get('Anio'),
                form.cleaned_data.get('Mes'),
                form.cleaned_data.get('Mes_Cobro'),
                form.cleaned_data.get('Consultor'),
                form.cleaned_data.get('LineaId'),
            ]
            if any(filtros):
                anio = form.cleaned_data['Anio']
                mes_factura = form.cleaned_data['Mes']  # Mes de facturación
                meses_cobro = form.cleaned_data['Mes_Cobro']  # Lista de meses a cobrar
                consultor = form.cleaned_data.get('Consultor')
                linea = form.cleaned_data.get('LineaId')

                # 1. Buscar registros existentes en Facturacion_Consultores para todos los meses seleccionados
                facturacion_existente = Facturacion_Consultores.objects.filter(
                    Anio=anio, Mes=mes_factura, Periodo_Cobrado__in=meses_cobro
                )
                if consultor:
                    facturacion_existente = facturacion_existente.filter(Documento=consultor)
                if linea:
                    facturacion_existente = facturacion_existente.filter(LineaId=linea)
                total_registros = facturacion_existente.count()
                facturacion_existente_page = facturacion_existente[(page-1)*page_size:page*page_size]
                for registro in facturacion_existente_page:
                    horas = registro.Horas
                    # Formatear para mostrar solo 1 decimal sin ceros adicionales
                    horas_formateadas = format(horas, '.1f').rstrip('0').rstrip('.') if horas is not None else ''
                    # Obtener porcentajes de IVA y Retención Fuente usando la función obtener_tarifa
                    porcentaje_iva = 0
                    porcentaje_retencion = 0
                    try:
                        tarifa = obtener_tarifa(registro.Anio, registro.Periodo_Cobrado, registro.Documento, registro.ClienteId)
                        if tarifa:
                            porcentaje_iva = float(tarifa.iva or 0)
                            porcentaje_retencion = float(tarifa.rteFte or 0)
                    except Exception:
                        pass
                    facturacion_info.append({
                        'id': registro.id,
                        'Anio': registro.Anio,
                        'Mes': registro.Mes,
                        'Consultor': registro.Documento.Nombre if hasattr(registro.Documento, 'Nombre') else str(registro.Documento),
                        'ConsultorId': registro.Documento.Documento if hasattr(registro.Documento, 'Documento') else registro.Documento,
                        'Empresa': registro.Empresa if hasattr(registro, 'Empresa') else '',
                        'Linea': registro.LineaId.Linea if hasattr(registro.LineaId, 'Linea') else str(registro.LineaId),
                        'LineaId': registro.LineaId.LineaId if hasattr(registro.LineaId, 'LineaId') else registro.LineaId,
                        'Numero_Factura': registro.Cta_Cobro,
                        'Periodo_Cobrado': registro.Periodo_Cobrado,
                        'Aprobado_Por': registro.Aprobado_Por,
                        'Fecha_Cobro': registro.Fecha_Cobro,
                        'Fecha_Pago': registro.Fecha_Pago,
                        'Cliente': registro.ClienteId.Nombre_Cliente if hasattr(registro.ClienteId, 'Nombre_Cliente') else str(registro.ClienteId),
                        'ClienteId': registro.ClienteId.ClienteId if hasattr(registro.ClienteId, 'ClienteId') else registro.ClienteId,
                        'Modulo': registro.ModuloId.Modulo if hasattr(registro.ModuloId, 'Modulo') else str(registro.ModuloId),
                        'ModuloId': registro.ModuloId.ModuloId if hasattr(registro.ModuloId, 'ModuloId') else registro.ModuloId,
                        'Cantidad_Horas': horas_formateadas,
                        'Valor_Unitario': registro.Valor_Unitario,
                        'Valor_Cobro': registro.Valor_Cobro,
                        'IVA': registro.IVA,
                        'Valor_Neto': registro.Valor_Neto,
                        'Retencion_Fuente': registro.Retencion_Fuente,
                        'Valor_Pagado': registro.Valor_Pagado,
                        'Factura': registro.Factura,
                        'Valor_Factura_Cliente': registro.Valor_Fcta_Cliente,
                        'Fecha': registro.Fecha,
                        'Porcentaje_Dif': registro.Dif,
                        'Diferencia_Bruta': registro.Diferencia_Bruta,
                        'Observaciones': registro.Observaciones,
                        'Deuda_Tecnica': registro.Deuda_Tecnica,
                        'Factura_Pendiente': registro.Factura_Pendiente,
                        'Porcentaje_IVA': porcentaje_iva,
                        'Porcentaje_Retencion': porcentaje_retencion,
                    })

                # 2. Buscar en Tiempos_Cliente los que NO están en Facturacion_Consultores para todos los meses seleccionados
                claves_facturadas = set(
                    (
                        r.Anio, r.Mes, str(r.Periodo_Cobrado), r.Documento_id, r.ClienteId_id, r.LineaId_id, r.ModuloId_id
                    ) for r in facturacion_existente
                )
                
                # Ordenar los meses en orden descendente (de mayor a menor)
                meses_cobro_ordenados = sorted(meses_cobro, reverse=True)
                
                # Procesar todos los registros de cada mes por separado
                for mes_cobro in meses_cobro_ordenados:
                    # Filtrar tiempos_clientes para cada mes_cobro
                    form.cleaned_data['Mes_Cobro'] = mes_cobro
                    tiempos_clientes = filtrar_tiempos_clientes(form)
                    
                    # Procesar todos los registros de este mes
                    registros_mes_actual = []
                    for tiempo in tiempos_clientes:
                        clave = (
                            anio,
                            mes_factura,
                            str(mes_cobro),
                            tiempo.Documento,
                            tiempo.ClienteId.ClienteId if hasattr(tiempo.ClienteId, 'ClienteId') else tiempo.ClienteId,
                            tiempo.LineaId.LineaId if hasattr(tiempo.LineaId, 'LineaId') else tiempo.LineaId,
                            tiempo.ModuloId.ModuloId if hasattr(tiempo.ModuloId, 'ModuloId') else tiempo.ModuloId,
                        )
                        if clave in claves_facturadas:
                            continue  # Ya está facturado
                        tarifa = obtener_tarifa(anio, mes_cobro, tiempo.Documento, tiempo.ClienteId)
                        if not tarifa:
                            continue
                        valor_hora = Decimal(tarifa.valorHora or 0)
                        porcentaje_iva = float(tarifa.iva or 0)
                        porcentaje_retencion = float(tarifa.rteFte or 0)
                        porcentaje_iva_decimal = Decimal(tarifa.iva or 0) / 100
                        porcentaje_retencion_decimal = Decimal(tarifa.rteFte or 0) / 100
                        horas = Decimal(tiempo.Horas or 0)
                        horas_formateadas = format(horas, '.1f').rstrip('0').rstrip('.') if horas else ''
                        valor_cobro = round(valor_hora * horas, 2)
                        iva = round(porcentaje_iva_decimal * valor_cobro, 2)
                        retencion = round(porcentaje_retencion_decimal * valor_cobro, 2)
                        valor_neto = round(valor_cobro + iva, 2)
                        valor_pagado = round(valor_neto - retencion, 2)
                        consultor_nombre = None
                        try:
                            consultor_obj = Consultores.objects.get(Documento=tiempo.Documento)
                            consultor_nombre = consultor_obj.Nombre
                        except Consultores.DoesNotExist:
                            consultor_nombre = str(tiempo.Documento)
                        
                        # Obtener la empresa del consultor
                        empresa_consultor = ''
                        try:
                            consultor_obj = Consultores.objects.get(Documento=tiempo.Documento)
                            empresa_consultor = consultor_obj.Empresa if hasattr(consultor_obj, 'Empresa') else ''
                        except Consultores.DoesNotExist:
                            empresa_consultor = ''
                        
                        # Agregar a la lista temporal de este mes
                        registros_mes_actual.append({
                            'id': 'new',
                            'Anio': anio,
                            'Mes': mes_factura,
                            'Consultor': consultor_nombre,
                            'ConsultorId': tiempo.Documento,
                            'Empresa': empresa_consultor,
                            'Linea': tiempo.LineaId.Linea if hasattr(tiempo.LineaId, 'Linea') else str(tiempo.LineaId),
                            'LineaId': tiempo.LineaId.LineaId if hasattr(tiempo.LineaId, 'LineaId') else tiempo.LineaId,
                            'Numero_Factura': '',
                            'Periodo_Cobrado': mes_cobro,
                            'Aprobado_Por': '',
                            'Fecha_Cobro': '',
                            'Fecha_Pago': '',
                            'Cliente': tiempo.ClienteId.Nombre_Cliente if hasattr(tiempo.ClienteId, 'Nombre_Cliente') else str(tiempo.ClienteId),
                            'ClienteId': tiempo.ClienteId.ClienteId if hasattr(tiempo.ClienteId, 'ClienteId') else tiempo.ClienteId,
                            'Modulo': tiempo.ModuloId.Modulo if hasattr(tiempo.ModuloId, 'Modulo') else str(tiempo.ModuloId),
                            'ModuloId': tiempo.ModuloId.ModuloId if hasattr(tiempo.ModuloId, 'ModuloId') else tiempo.ModuloId,
                            'Cantidad_Horas': horas_formateadas,
                            'Valor_Unitario': valor_hora,
                            'Valor_Cobro': valor_cobro,
                            'IVA': iva,
                            'Valor_Neto': valor_neto,
                            'Retencion_Fuente': retencion,
                            'Valor_Pagado': valor_pagado,
                            'Factura': '',
                            'Valor_Factura_Cliente': '',
                            'Fecha': '',
                            'Porcentaje_Dif': '',
                            'Diferencia_Bruta': '',
                            'Observaciones': '',
                            'Deuda_Tecnica': '',
                            'Factura_Pendiente': '',
                            'Porcentaje_IVA': porcentaje_iva,
                            'Porcentaje_Retencion': porcentaje_retencion,
                        })
                    
                    # Agregar todos los registros de este mes a la lista principal
                    facturacion_info.extend(registros_mes_actual)

                # Totales
                if facturacion_info:
                    totales_facturacion = {
                        'Total Valor Cobro': sum([float(row['Valor_Cobro']) for row in facturacion_info]),
                        'Total IVA': sum([float(row['IVA']) for row in facturacion_info]),
                        'Total Valor Pagado': sum([float(row['Valor_Pagado']) for row in facturacion_info]),
                    }
                else:
                    totales_facturacion = {}
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
        'facturacion_info': sorted(facturacion_info, key=lambda x: (-int(x['Periodo_Cobrado']) if x['Periodo_Cobrado'].isdigit() else 0, str(x['Consultor']).lower(), str(x['Cliente']).lower())),
        'TotalesFacturacion': totales_facturacion,
        'mensaje': mensaje,
        'total_paginas': total_paginas,
        'pagina_actual': page,
        'total_registros': total_registros,
    }
    return render(request, 'FacturacionConsultores/FacturacionConsultoresIndex.html', context)

def safe_decimal(value):
    try:
        if value in [None, '', 'None']:
            return Decimal('0')
        return Decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal('0')

@login_required
@verificar_permiso('can_manage_facturacion_consultores')
@csrf_exempt
def guardar_facturacion_consultores(request):
    if request.method == 'POST':
        try:
            # Obtener solo los índices de registros que fueron enviados (editados)
            indices = [
                key.split('_')[1] for key in request.POST.keys() if key.startswith('factura_')
            ]
            indices = list(set(indices))  # Evitar duplicados

            print(f"Registros recibidos para procesar: {len(indices)}")
            print(f"Índices: {indices}")

            if not indices:
                print("No hay registros para procesar")
                return redirect('facturacion_consultores_index')

            registros_procesados = 0
            for i in indices:
                row_id = request.POST.get(f'factura_{i}')
                
                # Verificar si realmente hay datos para guardar
                tiene_datos = False
                campos_editables = [
                    f'Numero_Factura_{i}', f'Aprobado_Por_{i}', f'Fecha_Cobro_{i}', 
                    f'Fecha_Pago_{i}', f'Cantidad_Horas_{i}', f'Valor_Unitario_{i}',
                    f'IVA_{i}', f'Retencion_Fuente_{i}', f'Factura_{i}', 
                    f'Valor_Factura_Cliente_{i}', f'Fecha_{i}', f'Deuda_Tecnica_{i}',
                    f'Factura_Pendiente_{i}', f'Observaciones_{i}'
                ]
                
                for campo in campos_editables:
                    valor = request.POST.get(campo, '')
                    if valor and valor.strip() != '':
                        tiene_datos = True
                        break
                
                # Solo procesar si hay datos reales para guardar
                if not tiene_datos and row_id == 'new':
                    print(f"Saltando registro {i} (nuevo sin datos)")
                    continue

                print(f"Procesando registro {i} (ID: {row_id})")

                # Obtener o crear instancia
                if row_id == 'new':
                    row = Facturacion_Consultores()
                else:
                    row = Facturacion_Consultores.objects.filter(id=row_id).first() or Facturacion_Consultores()
                    
                # Campos comunes con conversión de tipos
                anio_val = request.POST.get(f'Anio_{i}')
                row.Anio = int(anio_val) if anio_val and anio_val.isdigit() else None
                
                mes_val = request.POST.get(f'Mes_{i}')
                row.Mes = int(mes_val) if mes_val and mes_val.isdigit() else None
                
                row.Documento = Consultores.objects.get(Documento=request.POST.get(f'ConsultorId_{i}'))
                row.ClienteId = Clientes.objects.get(ClienteId=request.POST.get(f'ClienteId_{i}'))
                row.ModuloId = Modulo.objects.get(ModuloId=request.POST.get(f'ModuloId_{i}'))
                row.LineaId = Linea.objects.get(LineaId=request.POST.get(f'LineaId_{i}'))
                row.Empresa = request.POST.get(f'Empresa_{i}') or ''
                row.Cta_Cobro = request.POST.get(f'Numero_Factura_{i}') or ''
                row.Aprobado_Por = request.POST.get(f'Aprobado_Por_{i}') or ''
                
                # Fechas
                fecha_cobro = request.POST.get(f'Fecha_Cobro_{i}')
                row.Fecha_Cobro = fecha_cobro if fecha_cobro else date.today()
                
                fecha_pago = request.POST.get(f'Fecha_Pago_{i}')
                row.Fecha_Pago = fecha_pago if fecha_pago else date.today()
                
                row.Periodo_Cobrado = request.POST.get(f'Periodo_Cobrado_{i}') or ''
                row.Factura = request.POST.get(f'Factura_{i}') or ''
                
                fecha_val = request.POST.get(f'Fecha_{i}')
                row.Fecha = fecha_val if fecha_val else None
                
                row.Deuda_Tecnica = request.POST.get(f'Deuda_Tecnica_{i}') or ''
                row.Factura_Pendiente = request.POST.get(f'Factura_Pendiente_{i}') or ''
                row.Observaciones = request.POST.get(f'Observaciones_{i}') or ''

                # Campos decimales protegidos
                row.Horas = safe_decimal(request.POST.get(f'Cantidad_Horas_{i}'))
                row.Valor_Unitario = safe_decimal(request.POST.get(f'Valor_Unitario_{i}'))
                row.IVA = safe_decimal(request.POST.get(f'IVA_{i}'))
                row.Retencion_Fuente = safe_decimal(request.POST.get(f'Retencion_Fuente_{i}'))
                row.Valor_Cobro = safe_decimal(request.POST.get(f'Valor_Cobro_{i}'))
                row.Valor_Neto = float(safe_decimal(request.POST.get(f'Valor_Neto_{i}')))  # FloatField
                row.Valor_Pagado = safe_decimal(request.POST.get(f'Valor_Pagado_{i}'))
                row.Valor_Fcta_Cliente = safe_decimal(request.POST.get(f'Valor_Factura_Cliente_{i}'))

                # Cálculos
                valor_cliente = row.Valor_Fcta_Cliente
                valor_cobro = row.Valor_Cobro
                if valor_cliente == 0:
                    diferencia_bruta = Decimal('0')
                    porcentaje_dif = Decimal('0')
                else:
                    diferencia_bruta = valor_cliente - valor_cobro
                    porcentaje_dif = abs(diferencia_bruta / valor_cliente) * 100

                row.Diferencia_Bruta = diferencia_bruta
                row.Dif = porcentaje_dif

                row.save()
                registros_procesados += 1

            print(f"Registros procesados exitosamente: {registros_procesados}")
            return redirect('facturacion_consultores_index')

        except Exception as e:
            print(f"Error al guardar: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

@login_required
@verificar_permiso('can_manage_facturacion_consultores')
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