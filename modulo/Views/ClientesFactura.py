import json
import textwrap
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction   
from django.forms import ValidationError
from django.shortcuts import render
from modulo import models
from modulo.forms import FacturacionFilterForm
from modulo.models import Clientes, ClientesContratos, FacturacionClientes, Linea, Tarifa_Clientes
from collections import defaultdict
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery, F, IntegerField, Value, Q

@login_required
@verificar_permiso('can_manage_clientes_factura')
@transaction.atomic
def clientes_factura_guardar(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            rows = data.get('data', [])
            
            # Debug: imprimir datos recibidos
            print("Datos recibidos:", json.dumps(rows, indent=2))
                
            for row in rows:
                # Validar campos obligatorios
                required_fields = ['ClienteId', 'LineaId', 'Anio', 'Mes', 'ModuloId']
                if not all(key in row for key in required_fields):
                    print(f"Faltan campos obligatorios en: {row}")
                    continue  # Saltar filas que no tienen los campos obligatorios

                # Obtener el flag is_new_line (manejar tanto string como boolean)
                is_new_line = row.get('is_new_line', 'false')
                if isinstance(is_new_line, bool):
                    is_new_line = 'true' if is_new_line else 'false'
                is_new_line = is_new_line.lower() == 'true'

                # Función auxiliar mejorada para conversión de valores decimales
                def safe_decimal_convert(value):
                    try:
                        if value is None or str(value).lower() in ['', 'none', 'null', 'undefined', 'nan']:
                            return Decimal('0.0')
                        # Si ya es decimal, retornar directamente
                        if isinstance(value, Decimal):
                            return value
                        # Remover caracteres no numéricos excepto punto decimal y signo negativo
                        clean_value = ''.join(c for c in str(value) if c.isdigit() or c in ['.', '-'])
                        return Decimal(clean_value) if clean_value else Decimal('0.0')
                    except (ValueError, TypeError, InvalidOperation):
                        return Decimal('0.0')

                # Convertir valores de manera segura
                consecutivo_id = row.get('ConsecutivoId')
                if consecutivo_id is not None:
                    try:
                        consecutivo_id = int(consecutivo_id)
                    except (ValueError, TypeError):
                        consecutivo_id = None
                
                anio = int(safe_decimal_convert(row.get('Anio')))
                mes = int(safe_decimal_convert(row.get('Mes')))
                cliente_id = int(safe_decimal_convert(row.get('ClienteId')))
                linea_id = int(safe_decimal_convert(row.get('LineaId')))
                modulo_id = int(safe_decimal_convert(row.get('ModuloId')))
        
                horas_factura = safe_decimal_convert(row.get('Horas'))
                valor_horas = safe_decimal_convert(row.get('Valor_Horas'))
                dias_factura = safe_decimal_convert(row.get('Dias'))
                valor_dias = safe_decimal_convert(row.get('Valor_Dias'))
                mes_factura = safe_decimal_convert(row.get('Meses'))
                valor_meses = safe_decimal_convert(row.get('Valor_Meses'))
                bolsa = safe_decimal_convert(row.get('Bolsa'))
                valor_bolsa = safe_decimal_convert(row.get('Valor_Bolsa'))
                iva = safe_decimal_convert(row.get('IVA'))

                descripcion = row.get('Descripcion', "") or ""
                numero_factura = row.get('Numero_Factura', "") or ""
                referencia = row.get('Referencia', "") or ""
                ceco = row.get('Ceco', "") or ""
                sitio_serv = row.get('Sitio_Serv', "") or ""

                # Calcular el valor
                valor = Decimal('0.0')

                if not linea_id or not modulo_id:
                    print(f"[SKIP] Fila sin LineaId/ModuloId válidos: {row}")
                    continue

                if horas_factura:
                    valor += horas_factura * valor_horas
                if dias_factura:
                    valor += dias_factura * valor_dias
                if mes_factura:
                    valor += mes_factura * valor_meses
                if bolsa:
                    valor += bolsa * valor_bolsa

                # Verificar si los IDs existen en la base de datos
                try:
                    cliente = Clientes.objects.get(ClienteId=cliente_id)
                    linea = Linea.objects.get(LineaId=linea_id)
                    modulo = models.Modulo.objects.get(ModuloId=modulo_id)
                except (Clientes.DoesNotExist, Linea.DoesNotExist, models.Modulo.DoesNotExist) as e:
                    print(f"Error: {e}")
                    continue

                # Siempre guardar el registro, incluso si todos los valores son 0
                if consecutivo_id and not is_new_line:
                    try:
                        facturacion_cliente = FacturacionClientes.objects.get(ConsecutivoId=consecutivo_id)
                        
                        # Actualizar todos los campos
                        facturacion_cliente.HorasFactura = float(horas_factura) if horas_factura is not None else 0.0
                        facturacion_cliente.Valor_Horas = valor_horas
                        facturacion_cliente.DiasFactura = float(dias_factura) if dias_factura is not None else 0.0
                        facturacion_cliente.Valor_Dias = valor_dias
                        facturacion_cliente.MesFactura = float(mes_factura) if mes_factura is not None else 0.0
                        facturacion_cliente.Valor_Meses = valor_meses
                        facturacion_cliente.Valor = valor
                        facturacion_cliente.Descripcion = descripcion
                        facturacion_cliente.Factura = numero_factura
                        facturacion_cliente.Bolsa = bolsa
                        facturacion_cliente.Valor_Bolsa = valor_bolsa
                        facturacion_cliente.IVA = float(iva) if iva is not None else 0.0
                        facturacion_cliente.Referencia = referencia
                        facturacion_cliente.Ceco = ceco
                        facturacion_cliente.Sitio_Serv = sitio_serv
                        facturacion_cliente.save()
                        print(f"Registro actualizado: {consecutivo_id}")

                    except FacturacionClientes.DoesNotExist:
                        # Crear un nuevo registro si no existe
                        FacturacionClientes.objects.create(
                            Anio=anio,
                            Mes=mes,
                            ClienteId=cliente,
                            LineaId=linea,
                            ModuloId=modulo,
                            HorasFactura=float(horas_factura) if horas_factura is not None else 0.0,
                            Valor_Horas=valor_horas,
                            DiasFactura=float(dias_factura) if dias_factura is not None else 0.0,
                            Valor_Dias=valor_dias,
                            MesFactura=float(mes_factura) if mes_factura is not None else 0.0,
                            Valor_Meses=valor_meses,
                            Valor=valor,
                            Descripcion=descripcion,
                            Factura=numero_factura,
                            Bolsa=bolsa,
                            Valor_Bolsa=valor_bolsa,
                            IVA=float(iva) if iva is not None else 0.0,
                            Referencia=referencia,
                            Ceco=ceco,
                            Sitio_Serv=sitio_serv
                        )
                        print(f"Nuevo registro creado con ID existente: {consecutivo_id}")
                else:
                    # Para nuevas filas, usar create en lugar de update_or_create
                    FacturacionClientes.objects.create(
                        Anio=anio,
                        Mes=mes,
                        ClienteId=cliente,
                        LineaId=linea,
                        ModuloId=modulo,
                        HorasFactura=float(horas_factura) if horas_factura is not None else 0.0,
                        Valor_Horas=valor_horas,
                        DiasFactura=float(dias_factura) if dias_factura is not None else 0.0,
                        Valor_Dias=valor_dias,
                        MesFactura=float(mes_factura) if mes_factura is not None else 0.0,
                        Valor_Meses=valor_meses,
                        Valor=valor,
                        Descripcion=descripcion,
                        Factura=numero_factura,
                        Bolsa=bolsa,
                        Valor_Bolsa=valor_bolsa,
                        IVA=float(iva) if iva is not None else 0.0,
                        Referencia=referencia,
                        Ceco=ceco,
                        Sitio_Serv=sitio_serv
                    )
                    print("Nuevo registro creado")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"Error completo: {error_traceback}")
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'error': 'Método no permitido.'}, status=405)

@login_required
@verificar_permiso('can_manage_clientes_factura')
@csrf_exempt
def eliminar_facturas(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])
            FacturacionClientes.objects.filter(ConsecutivoId__in=ids).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

def filtrar_facturacion(form, clientes_contratos, facturacion_clientes):
    # Recuperar los filtros del formulario
    anio = form.cleaned_data.get('Anio')
    mes = form.cleaned_data.get('Mes')
    cliente_id = form.cleaned_data.get('ClienteId')
    linea_id = form.cleaned_data.get('LineaId')

    # Filtrar por los diferentes parámetros
    if anio:
        facturacion_clientes = facturacion_clientes.filter(Anio=anio)

    if mes:
        facturacion_clientes = facturacion_clientes.filter(Mes=mes)

    if cliente_id:
        clientes_contratos = clientes_contratos.filter(ClienteId=cliente_id)
        facturacion_clientes = facturacion_clientes.filter(ClienteId=cliente_id)

    if linea_id:
        facturacion_clientes = facturacion_clientes.filter(LineaId=linea_id)

    return clientes_contratos, facturacion_clientes

def obtener_info_facturacion(clientes_contratos, facturacion_clientes, anio, mes, linea_id=None):
    facturacion_info = []

    # Diccionario para rastrear las combinaciones de cliente, línea y módulo ya procesadas
    combinaciones_procesadas = set()

    # Procesar todos los contratos (vigentes y no vigentes)
    for contrato in clientes_contratos:
        # Verificar si el contrato está vigente o si tiene datos en facturación
        if contrato.ContratoVigente or facturacion_clientes.filter(ClienteId=contrato.ClienteId).exists():
            cliente_info = next((item for item in facturacion_info if item['ClienteId'] == contrato.ClienteId.ClienteId), None)
            if not cliente_info:
                cliente_info = {
                    'Cliente': contrato.ClienteId.Nombre_Cliente,
                    'ClienteId': contrato.ClienteId.ClienteId,
                    'Facturas': []
                }
                facturacion_info.append(cliente_info)

            # Obtener todas las tarifas para este cliente, año and mes
            tarifas = Tarifa_Clientes.objects.filter(
                clienteId=contrato.ClienteId,
                anio__lte=anio,  # Tarifas con año menor o igual al solicitado
                mes__lte=mes     # Tarifas con mes menor o igual al solicitado
            ).order_by('-anio', '-mes')  # Ordenar por año y mes descendente

            # Si no hay tarifas, continuar con el siguiente contrato
            if not tarifas.exists():
                continue

            if linea_id:  # <--- aplicar filtro de línea
                tarifas = tarifas.filter(lineaId_id=linea_id)

            # Procesar cada tarifa
            for tarifa in tarifas:
                # Crear una clave única para la combinación de cliente, línea y módulo
                clave_combinacion = (tarifa.clienteId.ClienteId, tarifa.lineaId.LineaId, tarifa.moduloId.ModuloId)

                # Si ya hemos procesado esta combinación, continuar con la siguiente tarifa
                if clave_combinacion in combinaciones_procesadas:
                    continue

                # Marcar esta combinación como procesada
                combinaciones_procesadas.add(clave_combinacion)

                # Obtener las facturaciones para esta tarifa (cliente, línea y módulo)
                facturaciones = facturacion_clientes.filter(
                    ClienteId=tarifa.clienteId,
                    LineaId=tarifa.lineaId,
                    ModuloId=tarifa.moduloId
                )

                # Si el contrato está vigente, mostrar datos vacíos si no hay facturaciones
                if contrato.ContratoVigente and not facturaciones.exists():
                    cliente_info['Facturas'].append({
                        'ConsecutivoId': '',
                        'LineaId': tarifa.lineaId.LineaId,
                        'Linea': tarifa.lineaId.Linea,
                        'ModuloId': tarifa.moduloId.ModuloId if tarifa.moduloId else None,
                        'Modulo': tarifa.moduloId.Modulo if tarifa.moduloId else '',
                        'Horas': '',
                        'Valor_Horas': tarifa.valorHora if tarifa else 0,
                        'Dias': '',
                        'Valor_Dias': tarifa.valorDia if tarifa else 0,
                        'Mes': '',
                        'Valor_Meses': tarifa.valorMes if tarifa else 0,
                        'Valor': 0,
                        'Descripcion': '',
                        'NumeroFactura': '',
                        'Bolsa': '',
                        'Valor_Bolsa': tarifa.valorBolsa if tarifa else 0,
                        'IVA': float(tarifa.iva) if (tarifa and tarifa.iva is not None) else 0,
                        'Referencia': tarifa.referenciaId.codigoReferencia if tarifa and tarifa.referenciaId else '',
                        'Ceco': tarifa.centrocostosId.codigoCeCo if tarifa and tarifa.centrocostosId else '',
                        'Sitio_Serv': tarifa.sitioTrabajo if tarifa else ''
                    })
                else:
                    # Procesar las facturaciones para esta tarifa
                    for facturacion in facturaciones:
                        # Obtener los valores de horas, días y meses
                        horas = facturacion.HorasFactura or 0
                        dias = facturacion.DiasFactura or 0
                        meses = facturacion.MesFactura or 0
                        bolsa = facturacion.Bolsa or 0

                        # Obtener los valores unitarios (Valor_Horas, Valor_Dias, Valor_Meses)
                        valor_horas = facturacion.Valor_Horas or (Decimal(str(tarifa.valorHora)) if tarifa and tarifa.valorHora is not None else Decimal('0.0'))
                        valor_dias = facturacion.Valor_Dias or (Decimal(str(tarifa.valorDia)) if tarifa and tarifa.valorDia is not None else Decimal('0.0'))
                        valor_meses = facturacion.Valor_Meses or (Decimal(str(tarifa.valorMes)) if tarifa and tarifa.valorMes is not None else Decimal('0.0'))
                        valor_bolsa = facturacion.Valor_Bolsa or (Decimal(str(tarifa.valorBolsa)) if tarifa and tarifa.valorBolsa is not None else Decimal('0.0'))

                        # Calcular el valor total
                        valor = (Decimal(horas) * valor_horas) + (Decimal(dias) * valor_dias) + (Decimal(meses) * valor_meses) + (Decimal(bolsa) * valor_bolsa)

                        cliente_info['Facturas'].append({
                            'ConsecutivoId': facturacion.ConsecutivoId,
                            'LineaId': tarifa.lineaId.LineaId,
                            'Linea': tarifa.lineaId.Linea,
                            'ModuloId': tarifa.moduloId.ModuloId if tarifa.moduloId else None,
                            'Modulo': tarifa.moduloId.Modulo if tarifa.moduloId else '',
                            'Horas': horas,
                            'Valor_Horas': valor_horas,
                            'Dias': dias,
                            'Valor_Dias': valor_dias,
                            'Mes': meses,
                            'Valor_Meses': valor_meses,
                            'Valor': valor,
                            'Descripcion': facturacion.Descripcion,
                            'NumeroFactura': facturacion.Factura,
                            'Bolsa': bolsa,
                            'Valor_Bolsa': valor_bolsa,
                            'IVA': facturacion.IVA or (float(tarifa.iva) if tarifa and tarifa.iva is not None else 0),
                            'Referencia': facturacion.Referencia or (tarifa.referenciaId.codigoReferencia if tarifa and tarifa.referenciaId else ''),
                            'Ceco': facturacion.Ceco or (tarifa.centrocostosId.codigoCeCo if tarifa and tarifa.centrocostosId else ''),
                            'Sitio_Serv': facturacion.Sitio_Serv or (tarifa.sitioTrabajo if tarifa else '')
                        })

            combos_tarifa = set()
            for t in tarifas:
                combos_tarifa.add((
                    t.clienteId.ClienteId,
                    t.lineaId.LineaId if t.lineaId else None,
                    t.moduloId.ModuloId if t.moduloId else None
                ))

            # Tomar todas las facturaciones del cliente (ya filtradas por año/mes en 'facturacion_clientes')
            facturaciones_restantes = facturacion_clientes.filter(ClienteId=contrato.ClienteId)
            if linea_id:
                facturaciones_restantes = facturaciones_restantes.filter(LineaId_id=linea_id)

            for f in facturaciones_restantes:
                combo_f = (
                    f.ClienteId.ClienteId if f.ClienteId else None,
                    f.LineaId.LineaId if f.LineaId else None,
                    f.ModuloId.ModuloId if f.ModuloId else None
                )

                # Si la combinación ya está cubierta por alguna tarifa, no la duplicamos
                if combo_f in combos_tarifa:
                    continue

                # Asegurar el contenedor para este cliente
                cliente_info = next((item for item in facturacion_info if item['ClienteId'] == contrato.ClienteId.ClienteId), None)
                if not cliente_info:
                    cliente_info = {
                        'Cliente': contrato.ClienteId.Nombre_Cliente,
                        'ClienteId': contrato.ClienteId.ClienteId,
                        'Facturas': []
                    }
                    facturacion_info.append(cliente_info)

                # Preparar valores desde la facturación
                horas = f.HorasFactura or 0
                dias = f.DiasFactura or 0
                meses = f.MesFactura or 0
                bolsa = f.Bolsa or 0

                valor_horas = f.Valor_Horas or Decimal('0.0')
                valor_dias = f.Valor_Dias or Decimal('0.0')
                valor_meses = f.Valor_Meses or Decimal('0.0')
                valor_bolsa = f.Valor_Bolsa or Decimal('0.0')

                valor_total = (Decimal(horas) * valor_horas) + (Decimal(dias) * valor_dias) + (Decimal(meses) * valor_meses) + (Decimal(bolsa) * valor_bolsa)

                cliente_info['Facturas'].append({
                    'ConsecutivoId': f.ConsecutivoId,
                    'LineaId': f.LineaId.LineaId if f.LineaId else None,
                    'Linea': f.LineaId.Linea if f.LineaId else '',
                    'ModuloId': f.ModuloId.ModuloId if f.ModuloId else None,
                    'Modulo': f.ModuloId.Modulo if f.ModuloId else '',
                    'Horas': horas,
                    'Valor_Horas': valor_horas,
                    'Dias': dias,
                    'Valor_Dias': valor_dias,
                    'Mes': meses,
                    'Valor_Meses': valor_meses,
                    'Bolsa': bolsa,
                    'Valor_Bolsa': valor_bolsa,
                    'Valor': valor_total,
                    'Descripcion': f.Descripcion or '',
                    'NumeroFactura': f.Factura or '',
                    'IVA': f.IVA or 0,
                    'Referencia': f.Referencia or '',
                    'Ceco': f.Ceco or '',
                    'Sitio_Serv': f.Sitio_Serv or ''
                })

    return facturacion_info

@login_required
@verificar_permiso('can_manage_clientes_factura')
def clientes_factura_index(request):
    clientes = models.Clientes.objects.all()
    lineas = models.Linea.objects.all()
    modulos = models.Modulo.objects.all()
    clientes_contratos = models.ClientesContratos.objects.all()
    facturacion_clientes = models.FacturacionClientes.objects.all()

    # Inicializar facturacion_info con una lista vacía
    facturacion_info = []
    totales_facturacion = {}

    if request.method == 'GET':
        form = FacturacionFilterForm(request.GET)

        if form.is_valid():
            anio = form.cleaned_data.get('Anio')
            mes = form.cleaned_data.get('Mes')
            linea_id = form.cleaned_data.get('LineaId')
            # Filtrar facturación según los datos del formulario
            clientes_contratos, facturacion_clientes = filtrar_facturacion(form, clientes_contratos, facturacion_clientes)

            # Obtener la información de facturación
            facturacion_info = obtener_info_facturacion(clientes_contratos, facturacion_clientes, anio, mes, linea_id)

            # Debug: imprimir facturacion_info para verificar los datos
            print(f"DEBUG - facturacion_info: {facturacion_info}")

            # Calcular totales
            totales_facturacion = calcular_totales_facturacion(facturacion_info)

    else:
        form = FacturacionFilterForm()

    context = {
        'form': form,
        'facturacion_info': facturacion_info,
        'Clientes': clientes,
        'Lineas': lineas,
        'Modulos': modulos,
        'TotalesFacturacion': totales_facturacion,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not facturacion_info else ""
    }

    return render(request, 'Clientesfactura/Clientesfacturaindex.html', context)

def calcular_totales_facturacion(facturacion_info):
    totales = {
        'Total_Horas': 0.0,
        'Total_Dias': 0.0,
        'Total_Meses': 0,
        'Total_Bolsa': Decimal('0.0'),
        'Total_Valor': Decimal('0.0'),
    }
    
    for cliente in facturacion_info:
        for factura in cliente['Facturas']:
            # Sumar valores de cada factura
            print(f"DEBUG - Factura: {factura}")

            totales['Total_Horas'] += factura.get('Horas', 0) or 0.0
            totales['Total_Dias'] += factura.get('Dias', 0) or 0.0
            totales['Total_Meses'] += factura.get('Mes', 0) or 0
            
            # Convertir y sumar valores Decimal
            bolsa = Decimal(str(factura.get('Bolsa', 0))) if factura.get('Bolsa') not in [None, ''] else Decimal('0.0')
            valor = Decimal(str(factura.get('Valor', 0))) if factura.get('Valor') not in [None, ''] else Decimal('0.0')
            
            totales['Total_Bolsa'] += bolsa
            totales['Total_Valor'] += valor
            print(f"DEBUG - Totales calculados: {totales}")

    
    return totales

@login_required
@verificar_permiso('can_manage_clientes_factura')
@csrf_exempt
def generar_plantilla(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            format_type = data.get('format', 'xlsx')
            rows = data.get('data', [])
            df = pd.DataFrame(rows)

            if format_type == 'xlsx':
                matplotlib.use('Agg') 
                # Generar Excel con formato profesional
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Facturación')
                    
                    workbook = writer.book
                    worksheet = writer.sheets['Facturación']
                    
                    # Formato de cabecera mejorado
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'vcenter',
                        'fg_color': '#4F81BD',
                        'font_color': 'white',
                        'border': 1,
                        'font_size': 12
                    })
                    
                    # Formato monetario profesional
                    money_format = workbook.add_format({
                        'num_format': '"$"#,##0.00',
                        'font_size': 11,
                        'border': 1
                    })
                    
                    # Ajuste inteligente de columnas
                    for idx, col in enumerate(df.columns):
                        # Calcular ancho basado en contenido
                        max_data_len = df[col].astype(str).apply(len).max()
                        max_header_len = len(str(col))
                        max_len = max(max_data_len, max_header_len)
                        
                        # Conversión a unidades Excel (1 unidad ≈ 1 carácter en Calibri 11)
                        excel_width = (max_len * 1.2) + 2  # Fórmula mejorada
                        
                        # Limitar ancho máximo a 50
                        worksheet.set_column(idx, idx, min(excel_width, 50))
                        
                        # Aplicar formato monetario
                        if col in ['Valor Unitario', 'Valor Total', 'Valor_Unitario', 'Valor_Total']:
                            worksheet.set_column(idx, idx, 15, money_format)
                    
                    # Aplicar formato de cabecera
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    # Congelar cabeceras y añadir filtros
                    worksheet.autofilter(0, 0, 0, len(df.columns)-1)
                    worksheet.freeze_panes(1, 0)
                    worksheet.set_zoom(90)

                output.seek(0)

                # Limpiar explícitamente la figura
                plt.close('all')  # <--- Añadir esto para liberar memoria
                matplotlib.pyplot.close('all')  # <--- Doble limpieza por seguridad

                response = HttpResponse(
                    output.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=plantilla_profesional.xlsx'
                return response

            elif format_type == 'jpg':
                matplotlib.use('Agg') 

                # Preparar datos para imagen
                df_jpg = df.copy()
                
                # Aplicar wrap de texto a cadenas largas
                text_columns = ['Concepto', 'Referencia', 'Sitio Servicio']
                for col in text_columns:
                    if col in df_jpg.columns:
                        df_jpg[col] = df_jpg[col].apply(
                            lambda x: '\n'.join(textwrap.wrap(str(x), width=20)) if isinstance(x, str) else x
                        )
                
                # Calcular dimensiones dinámicas
                num_cols = len(df_jpg.columns)
                num_rows = len(df_jpg)
                
                # Tamaño base + ajuste por contenido
                fig_width = max(12, num_cols * 2.5)  # 2.5 pulgadas por columna
                fig_height = 4 + (num_rows * 0.3)    # 0.3 pulgadas por fila
                
                plt.figure(figsize=(fig_width, fig_height), dpi=200)
                ax = plt.subplot(frame_on=False)
                ax.axis('off')
                
                # Crear tabla con estilo profesional
                tbl = plt.table(
                    cellText=df_jpg.values,
                    colLabels=df_jpg.columns,
                    cellLoc='center',
                    loc='center',
                    colColours=['#4F81BD']*num_cols,
                    colWidths=[0.18]*num_cols  # Ancho relativo por columna
                )
                
                # Autoajustar fuente y tamaño
                tbl.auto_set_font_size(True)
                tbl.set_fontsize(10)
                
                # Ajustar escalas y espacios
                tbl.scale(1, 2)  # Ampliar espacio vertical
                plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                
                # Color alternado para filas
                for i in range(1, num_rows+1):
                    for j in [0, num_cols-1]:  # Colorear primera y última columna
                        tbl[(i, j)].set_facecolor('#E6E6E6')
                
                # Guardar imagen de alta calidad
                img_buffer = BytesIO()
                plt.savefig(img_buffer, 
                           format='jpg', 
                           bbox_inches='tight',
                           pad_inches=0.3,
                           dpi=300)
                
                # Limpiar explícitamente la figura
                plt.close('all')  # <--- Añadir esto para liberar memoria
                matplotlib.pyplot.close('all')  # <--- Doble limpieza por seguridad
                
                response = HttpResponse(
                    img_buffer.getvalue(),
                    content_type='Image/Jpeg'
                )
                response['Content-Disposition'] = 'attachment; filename=plantilla_profesional.jpg'
                return response

            else:
                return HttpResponse('Formato no soportado', status=400)

        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)
    return HttpResponse('Método no permitido', status=405)

@login_required
@verificar_permiso('can_manage_clientes_factura')
def obtener_tarifa(request): 
    try:
        # Obtener los parámetros de la solicitud
        cliente_id = request.GET.get('clienteId')
        linea_id = request.GET.get('lineaId')
        modulo_id = request.GET.get('moduloId')
        anio = request.GET.get('anio')
        mes = request.GET.get('mes')

        # Validar que los parámetros sean números enteros
        if not cliente_id or not linea_id or not anio or not mes or not modulo_id:
            return JsonResponse({'error': 'Los parámetros clienteId, lineaId, anio, mes y modulo son requeridos.'}, status=400)
        
        try:
            cliente_id = int(cliente_id)
            linea_id = int(linea_id)
            modulo_id = int(modulo_id)
            anio = int(anio)
            mes = int(mes)
        except ValueError:
            return JsonResponse({'error': 'clienteId, lineaId, anio, mes y moduloId deben ser números enteros.'}, status=400)

        # Buscar la tarifa más reciente (año y mes anteriores o iguales)
        tarifa = Tarifa_Clientes.objects.filter(
            clienteId=cliente_id,
            lineaId=linea_id,
            moduloId=modulo_id,
            anio__lte=anio,
            mes__lte=mes
        ).order_by('-anio', '-mes').first()

        # Si no se encuentra tarifa, buscar cualquier tarifa del cliente
        if not tarifa:
            tarifa = Tarifa_Clientes.objects.filter(
                clienteId=cliente_id,
                lineaId=linea_id,
                moduloId=modulo_id
            ).order_by('-anio', '-mes').first()

        # Construir respuesta
        if tarifa:
            data = {
                'valorHora': str(Decimal(tarifa.valorHora)) if tarifa.valorHora else '0.0',
                'valorDia': str(Decimal(tarifa.valorDia)) if tarifa.valorDia else '0.0',
                'valorMes': str(Decimal(tarifa.valorMes)) if tarifa.valorMes else '0.0',
                'valorBolsa': str(Decimal(tarifa.valorBolsa)) if tarifa.valorBolsa else '0.0',
                'iva': float(tarifa.iva) if tarifa.iva is not None else 0.0,
                'referenciaId': {
                    'codigoReferencia': tarifa.referenciaId.codigoReferencia if tarifa.referenciaId else ''
                },
                'centrocostosId': {
                    'codigoCeCo': tarifa.centrocostosId.codigoCeCo if tarifa.centrocostosId else ''
                },
                'sitioTrabajo': tarifa.sitioTrabajo if tarifa.sitioTrabajo else ''
            }
        else:
            # Datos por defecto si no hay ninguna tarifa
            data = {
                'valorHora': '0.0',
                'valorDia': '0.0',
                'valorMes': '0.0',
                'valorBolsa': '0.0',
                'iva': 0.0,
                'referenciaId': {'codigoReferencia': ''},
                'centrocostosId': {'codigoCeCo': ''},
                'sitioTrabajo': ''
            }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)

@login_required
@verificar_permiso('can_manage_clientes_factura')
def get_lineas_modulos(request):
    cliente_id = request.GET.get('clienteId')
    anio = request.GET.get('anio')  # ya no se usa para filtrar, se mantiene por compatibilidad
    mes = request.GET.get('mes')    # idem
    linea_id = request.GET.get('lineaId')

    if not cliente_id:
        return JsonResponse({'error': 'ClienteId es requerido.'}, status=400)

    try:
        cliente_id = int(cliente_id)
        linea_id_int = int(linea_id) if linea_id else None

        # Base: todas las tarifas del cliente (y opcionalmente de la línea)
        base_qs = (Tarifa_Clientes.objects
                   .filter(clienteId=cliente_id)
                   .select_related('lineaId', 'moduloId'))

        if linea_id_int:
            base_qs = base_qs.filter(lineaId=linea_id_int)

        # Subquery: para cada (linea, modulo) tomar el PK de la tarifa más reciente (anio, mes) 
        latest_pk_sq = (Tarifa_Clientes.objects
            .filter(
                clienteId=cliente_id,
                lineaId=OuterRef('lineaId'),
                moduloId=OuterRef('moduloId'),
                # si quieres además respetar "no en el futuro" respecto al filtro Anio/Mes,
                # descomenta estas dos líneas:
                # anio__lte=int(anio) if anio else None,
                # mes__lte=int(mes) if mes else None,
            )
            .order_by('-anio', '-mes')
            .values('pk')[:1])

        # Lista final: solo los registros cuyo pk = último de su par (linea, modulo)
        latest_qs = base_qs.filter(pk__in=Subquery(
            base_qs.values('lineaId', 'moduloId').annotate(
                last_id=Subquery(latest_pk_sq)
            ).values('last_id')
        ))

        # Construir listas únicas para el modal
        lineas, modulos = [], []
        seen_lineas, seen_modulos = set(), set()

        for t in latest_qs:
            if t.lineaId and t.lineaId.LineaId not in seen_lineas:
                lineas.append({'LineaId': t.lineaId.LineaId, 'Linea': t.lineaId.Linea})
                seen_lineas.add(t.lineaId.LineaId)
            if t.moduloId and t.moduloId.ModuloId not in seen_modulos:
                modulos.append({'ModuloId': t.moduloId.ModuloId, 'Modulo': t.moduloId.Modulo})
                seen_modulos.add(t.moduloId.ModuloId)

        return JsonResponse({'lineas': lineas, 'modulos': modulos})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)