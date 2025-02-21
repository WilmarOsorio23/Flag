import json
import textwrap
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import render
from Modulo import models
from Modulo.forms import FacturacionFilterForm
from Modulo.models import Clientes, ClientesContratos, FacturacionClientes, Linea, Tarifa_Clientes
from collections import defaultdict

@transaction.atomic
def clientes_factura_guardar(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rows = data.get('data', [])
            # Aquí puedes procesar cada fila
            for row in rows:
                # Validar campos obligatorios
                if not all(key in row for key in ['ClienteId', 'LineaId', 'Anio', 'Mes','ModuloId']):
                    continue  # Saltar filas que no tienen los campos obligatorios

                # Convertir valores de manera segura
                consecutivo_id = row.get('ConsecutivoId') or None
                anio = int(row.get('Anio', 0)) if row.get('Anio') else 0
                mes = int(row.get('Mes', 0)) if row.get('Mes') else 0
                cliente_id = int(row.get('ClienteId', 0)) if row.get('ClienteId') else 0
                linea_id = int(row.get('LineaId', 0)) if row.get('LineaId') else 0
                modulo_id = int(row.get('ModuloId', 0)) if row.get('ModuloId') else 0
                
                horas_factura = float(row.get('Horas', 0)) if row.get('Horas') else 0.0
                valor_horas = float(row.get('Valor_Horas', 0)) if row.get('Valor_Horas') else 0.0
                dias_factura = float(row.get('Dias', 0)) if row.get('Dias') else 0.0
                valor_dias = float(row.get('Valor_Dias', 0)) if row.get('Valor_Dias') else 0.0
                mes_factura = int(row.get('Meses', 0)) if row.get('Meses') else 0
                valor_meses = float(row.get('Valor_Meses', 0)) if row.get('Valor_Meses') else 0.0

                bolsa = float(row.get('Bolsa', 0)) if row.get('Bolsa') else 0.0
                valor_bolsa = float(row.get('Valor_Bolsa', 0)) if row.get('Valor_Bolsa') else 0.0

                iva = float(row.get('IVA', 0)) if row.get('IVA') else 0.0

                descripcion = row.get('Descripcion', "") or ""
                numero_factura = row.get('Numero_Factura', "") or ""
                referencia = row.get('Referencia', "") or ""
                ceco = row.get('Ceco', "") or ""
                sitio_serv = row.get('Sitio_Serv', "") or ""

                # Calcular el valor
                valor = (horas_factura * valor_horas if horas_factura else 0) + (dias_factura * valor_dias if dias_factura else 0) + (mes_factura * valor_meses if valor_meses else 0) + (bolsa * valor_bolsa if bolsa else 0)

                if (horas_factura > 0 or dias_factura > 0 or mes_factura > 0 or bolsa > 0):
                    # Verificar si el registro ya existe
                    if consecutivo_id:
                        try:
                            facturacion_cliente = FacturacionClientes.objects.get(
                                ConsecutivoId=consecutivo_id,
                                Anio=anio,
                                Mes=mes,
                                ClienteId=cliente_id,
                                LineaId=linea_id,
                                ModuloId=modulo_id
                            )
                            
                            # Verificar si los datos han cambiado
                            if (facturacion_cliente.HorasFactura == horas_factura and
                                facturacion_cliente.Valor_Horas == valor_horas and
                                facturacion_cliente.DiasFactura == dias_factura and
                                facturacion_cliente.Valor_Dias == valor_dias and
                                facturacion_cliente.MesFactura == mes_factura and
                                facturacion_cliente.Valor_Meses == valor_meses and
                                facturacion_cliente.Valor == valor and
                                facturacion_cliente.Descripcion == descripcion and
                                facturacion_cliente.Factura == numero_factura and
                                facturacion_cliente.Bolsa == bolsa and
                                facturacion_cliente.Valor_Bolsa == valor_bolsa and
                                facturacion_cliente.IVA == iva and
                                facturacion_cliente.Referencia == referencia and
                                facturacion_cliente.Ceco == ceco and
                                facturacion_cliente.Sitio_Serv == sitio_serv):
                                continue

                            # Actualizar solo si hay cambios
                            facturacion_cliente.HorasFactura = horas_factura
                            facturacion_cliente.Valor_Horas = valor_horas
                            facturacion_cliente.DiasFactura = dias_factura
                            facturacion_cliente.Valor_Dias = valor_dias
                            facturacion_cliente.MesFactura = mes_factura
                            facturacion_cliente.Valor_Meses = valor_meses
                            facturacion_cliente.Valor = valor
                            facturacion_cliente.Descripcion = descripcion
                            facturacion_cliente.Factura = numero_factura
                            facturacion_cliente.Bolsa = bolsa
                            facturacion_cliente.Valor_Bolsa = valor_bolsa
                            facturacion_cliente.IVA = iva
                            facturacion_cliente.Referencia = referencia
                            facturacion_cliente.Ceco = ceco
                            facturacion_cliente.Sitio_Serv = sitio_serv
                            facturacion_cliente.save()

                        except FacturacionClientes.DoesNotExist:
                            # Crear un nuevo registro
                            FacturacionClientes.objects.create(
                                Anio=anio,
                                Mes=mes,
                                ClienteId_id=cliente_id,
                                LineaId_id=linea_id,
                                ModuloId_id=modulo_id,
                                HorasFactura=horas_factura,
                                Valor_Horas=valor_horas,
                                DiasFactura=dias_factura,
                                Valor_Dias=valor_dias,
                                MesFactura=mes_factura,
                                Valor_Meses=valor_meses,
                                Valor=valor,
                                Descripcion=descripcion,
                                Factura=numero_factura,
                                Bolsa=bolsa,
                                Valor_Bolsa=valor_bolsa,
                                IVA=iva,
                                Referencia=referencia,
                                Ceco=ceco,
                                Sitio_Serv=sitio_serv
                            )

                    else:
                        # Crear un nuevo registro solo si no se encontró el anterior
                        FacturacionClientes.objects.create(
                            Anio=anio,
                            Mes=mes,
                            ClienteId_id=cliente_id,
                            LineaId_id=linea_id,
                            ModuloId_id=modulo_id,
                            HorasFactura=horas_factura,
                            Valor_Horas=valor_horas,
                            DiasFactura=dias_factura,
                            Valor_Dias=valor_dias,
                            MesFactura=mes_factura,
                            Valor_Meses=valor_meses,
                            Valor=valor,
                            Descripcion=descripcion,
                            Factura=numero_factura,
                            Bolsa=bolsa,
                            Valor_Bolsa=valor_bolsa,
                            IVA=iva,
                            Referencia=referencia,
                            Ceco=ceco,
                            Sitio_Serv=sitio_serv
                        )
                else:
                    continue

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'error': 'Método no permitido.'}, status=405)

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

def obtener_info_facturacion(clientes_contratos, facturacion_clientes, anio, mes):
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

            # Obtener todas las tarifas para este cliente, año y mes
            tarifas = Tarifa_Clientes.objects.filter(
                clienteId=contrato.ClienteId,
                anio__lte=anio,  # Tarifas con año menor o igual al solicitado
                mes__lte=mes     # Tarifas con mes menor o igual al solicitado
            ).order_by('-anio', '-mes')  # Ordenar por año y mes descendente

            # Si no hay tarifas, continuar con el siguiente contrato
            if not tarifas.exists():
                continue

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
                        'IVA': tarifa.iva if tarifa else 0,
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
                        valor_horas = facturacion.Valor_Horas or (float(tarifa.valorHora) if tarifa and tarifa.valorHora is not None else 0)
                        valor_dias = facturacion.Valor_Dias or (float(tarifa.valorDia) if tarifa and tarifa.valorDia is not None else 0)
                        valor_meses = facturacion.Valor_Meses or (float(tarifa.valorMes) if tarifa and tarifa.valorMes is not None else 0)
                        valor_bolsa = facturacion.Valor_Bolsa or (float(tarifa.valorBolsa) if tarifa and tarifa.valorBolsa is not None else 0)

                        # Calcular el valor total
                        valor = (horas * float(valor_horas)) + (dias * float(valor_dias)) + (meses * float(valor_meses)) + (bolsa * float(valor_bolsa))

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
                            'IVA': facturacion.IVA or (tarifa.iva if tarifa else 0),
                            'Referencia': facturacion.Referencia or (tarifa.referenciaId.codigoReferencia if tarifa and tarifa.referenciaId else ''),
                            'Ceco': facturacion.Ceco or (tarifa.centrocostosId.codigoCeCo if tarifa and tarifa.centrocostosId else ''),
                            'Sitio_Serv': facturacion.Sitio_Serv or (tarifa.sitioTrabajo if tarifa else '')
                        })

    return facturacion_info

def clientes_factura_index(request):
    clientes = models.Clientes.objects.all()
    lineas = models.Linea.objects.all()
    clientes_contratos = models.ClientesContratos.objects.all()
    facturacion_clientes = models.FacturacionClientes.objects.all()

    if request.method == 'GET':
        form = FacturacionFilterForm(request.GET)

        if form.is_valid():
            anio = form.cleaned_data.get('Anio')
            mes = form.cleaned_data.get('Mes')
            
            # Filtrar facturación según los datos del formulario
            clientes_contratos, facturacion_clientes = filtrar_facturacion(form, clientes_contratos, facturacion_clientes)

            # Obtener la información de facturación
            facturacion_info = obtener_info_facturacion(clientes_contratos, facturacion_clientes, anio, mes)

            # Calcular totales
            totales_facturacion = calcular_totales_facturacion(facturacion_clientes)

    else:
        form = FacturacionFilterForm()
        facturacion_info = []
        totales_facturacion = {}

    context = {
        'form': form,
        'facturacion_info': facturacion_info,
        'Clientes': clientes,
        'Lineas': lineas,
        'TotalesFacturacion': totales_facturacion,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not facturacion_info else ""
    }

    return render(request, 'Clientes_Factura/clientes_factura_index.html', context)

def calcular_totales_facturacion(facturacion_clientes):
    totales = defaultdict(float)
    
    for factura in facturacion_clientes:
        totales['Total_Horas'] += factura.HorasFactura or 0
        totales['Total_Dias'] += factura.DiasFactura or 0
        totales['Total_Meses'] += factura.MesFactura or 0
        totales['Total_Bolsa'] += factura.Bolsa or 0
        totales['Total_Valor'] += factura.Valor or 0

    return totales

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
                        if col in ['Valor Unitario', 'Valor Total']:
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
                    content_type='image/jpeg'
                )
                response['Content-Disposition'] = 'attachment; filename=plantilla_profesional.jpg'
                return response

            else:
                return HttpResponse('Formato no soportado', status=400)

        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)
    return HttpResponse('Método no permitido', status=405)

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

       # Buscar la tarifa en la base de datos
        try:
            tarifa = Tarifa_Clientes.objects.get(clienteId=cliente_id, lineaId=linea_id, moduloId=modulo_id, anio=anio, mes=mes)
            # Construir la respuesta JSON con los datos de la tarifa encontrada
            data = {
                'valorHora': float(tarifa.valorHora) if tarifa.valorHora else 0.0,
                'valorDia': float(tarifa.valorDia) if tarifa.valorDia else 0.0,
                'valorMes': float(tarifa.valorMes) if tarifa.valorMes else 0.0,
                'valorBolsa': float(tarifa.valorBolsa) if tarifa.valorBolsa else 0.0,
                'iva': float(tarifa.iva) if tarifa.iva else 0.0,
                'referenciaId': {
                    'codigoReferencia': tarifa.referenciaId.codigoReferencia if tarifa.referenciaId else ''
                },
                'centrocostosId': {
                    'codigoCeCo': tarifa.centrocostosId.codigoCeCo if tarifa.centrocostosId else ''
                },
                'sitioTrabajo': tarifa.sitioTrabajo if tarifa.sitioTrabajo else ''
            }
        except Tarifa_Clientes.DoesNotExist:
            # Si no se encuentra la tarifa, devolver un objeto con valores vacíos
            data = {
                'valorHora': 0.0,
                'valorDia': 0.0,
                'valorMes': 0.0,
                'valorBolsa': 0.0,
                'iva': 0.0,
                'referenciaId': {
                    'codigoReferencia': ''
                },
                'centrocostosId': {
                    'codigoCeCo': ''
                },
                'sitioTrabajo': ''
            }

        return JsonResponse(data)

    except Exception as e:
        # Manejar cualquier otro error inesperado
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)