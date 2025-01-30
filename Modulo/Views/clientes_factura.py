# Vista para listar empleados
import json
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from Modulo import models
from Modulo.forms import FacturacionFilterForm
from Modulo.models import Clientes, ClientesContratos, FacturacionClientes, Linea
from collections import defaultdict
from django.db import transaction

@transaction.atomic
def clientes_factura_guardar(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rows = data.get('data', [])
            # Aquí puedes procesar cada fila
            for row in rows:
                consecutivo_id = row.get('ConsecutivoId')
                anio = int(row.get('Anio', 0))  # Convertir a int
                mes = int(row.get('Mes', 0))  # Convertir a int
                cliente_id = int(row.get('ClienteId', 0))  # Convertir a int
                linea_id = int(row.get('LineaId', 0))  # Convertir a int
                
                horas_factura = float(row.get('Horas', 0) or 0)  # Convertir a float
                dias_factura = row.get('Dias')
                dias_factura = float(dias_factura) if dias_factura and dias_factura != "None" else None  # Manejar None correctamente
                
                mes_factura = str(row.get('Meses', ""))  # Asegurar que sea texto
                valor = float(row.get('Valor', 0) or 0)  # Convertir a float
                descripcion = row.get('Descripcion', "")
                numero_factura = row.get('Numero_Factura', "")

                # Verificar que al menos uno de los campos tenga datos válidos
                if not (horas_factura or dias_factura or mes_factura.strip()):
                    continue

                # Verificar si el registro ya existe
                if consecutivo_id:
                    try:
                        facturacion_cliente = FacturacionClientes.objects.get(
                            ConsecutivoId=consecutivo_id,
                            Anio=anio,
                            Mes=mes,
                            ClienteId=cliente_id,
                            LineaId=linea_id
                        )

                        # Verificar si los datos han cambiado
                        if (facturacion_cliente.HorasFactura == horas_factura and
                            facturacion_cliente.DiasFactura == dias_factura and
                            facturacion_cliente.MesFactura == mes_factura and
                            facturacion_cliente.Valor == valor and
                            facturacion_cliente.Descripcion == descripcion and
                            facturacion_cliente.Factura == numero_factura):
                            continue

                        # Actualizar solo si hay cambios
                        facturacion_cliente.HorasFactura = horas_factura
                        facturacion_cliente.DiasFactura = dias_factura
                        facturacion_cliente.MesFactura = mes_factura
                        facturacion_cliente.Valor = valor
                        facturacion_cliente.Descripcion = descripcion
                        facturacion_cliente.Factura = numero_factura
                        facturacion_cliente.save()

                    except FacturacionClientes.DoesNotExist:
                        # Crear un nuevo registro
                        FacturacionClientes.objects.create(
                            Anio=anio,
                            Mes=mes,
                            ClienteId_id=cliente_id,  # _id para claves foráneas
                            LineaId_id=linea_id,  # _id para claves foráneas
                            HorasFactura=horas_factura,
                            DiasFactura=dias_factura,
                            MesFactura=mes_factura,
                            Valor=valor,
                            Descripcion=descripcion,
                            Factura=numero_factura
                        )

                else:
                    # Crear un nuevo registro solo si no se encontró el anterior
                    FacturacionClientes.objects.create(
                        Anio=anio,
                        Mes=mes,
                        ClienteId_id=cliente_id,  # _id para claves foráneas
                        LineaId_id=linea_id,  # _id para claves foráneas
                        HorasFactura=horas_factura,
                        DiasFactura=dias_factura,
                        MesFactura=mes_factura,
                        Valor=valor,
                        Descripcion=descripcion,
                        Factura=numero_factura
                    )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})
    return JsonResponse({'status': 'error', 'error': 'Método no permitido.'})

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
        clientes_contratos = clientes_contratos.filter(LineaId=linea_id)
        facturacion_clientes = facturacion_clientes.filter(LineaId=linea_id)

    return clientes_contratos, facturacion_clientes

def obtener_info_facturacion(clientes_contratos, facturacion_clientes):
    facturacion_info = []

    # Crear un diccionario para acceder rápidamente a los contratos por cliente y línea
    contratos_dict = {(contrato.ClienteId.ClienteId, contrato.LineaId.LineaId): contrato for contrato in clientes_contratos}

    # Procesar los contratos
    for contrato in clientes_contratos:
        cliente_info = next((item for item in facturacion_info if item['ClienteId'] == contrato.ClienteId.ClienteId), None)
        if not cliente_info:
            cliente_info = {
                'Cliente': contrato.ClienteId.Nombre_Cliente,
                'ClienteId': contrato.ClienteId.ClienteId,
                'Facturas': []
            }
            facturacion_info.append(cliente_info)

        facturaciones = facturacion_clientes.filter(
            ClienteId=contrato.ClienteId,
            LineaId=contrato.LineaId
        )

        if facturaciones.exists():
            for facturacion in facturaciones:
                cliente_info['Facturas'].append({
                    'ConsecutivoId': facturacion.ConsecutivoId,
                    'LineaId': contrato.LineaId.LineaId,
                    'Linea': contrato.LineaId.Linea,
                    'Horas': facturacion.HorasFactura,
                    'Dias': facturacion.DiasFactura,
                    'Mes': facturacion.MesFactura,
                    'Valor': facturacion.Valor,
                    'Descripcion': facturacion.Descripcion,
                    'NumeroFactura': facturacion.Factura
                })
        else:
            cliente_info['Facturas'].append({
                'ConsecutivoId': '',
                'LineaId': contrato.LineaId.LineaId,
                'Linea': contrato.LineaId.Linea,
                'Horas': '',
                'Dias': '',
                'Mes': '',
                'Valor': '',
                'Descripcion': '',
                'NumeroFactura': ''
            })

    # Procesar las facturaciones que no están en contratos
    for facturacion in facturacion_clientes:
        if (facturacion.ClienteId.ClienteId, facturacion.LineaId.LineaId) not in contratos_dict:
            cliente_info = next((item for item in facturacion_info if item['ClienteId'] == facturacion.ClienteId.ClienteId), None)
            if not cliente_info:
                cliente_info = {
                    'Cliente': facturacion.ClienteId.Nombre_Cliente,
                    'ClienteId': facturacion.ClienteId.ClienteId,
                    'Facturas': []
                }
                facturacion_info.append(cliente_info)

            cliente_info['Facturas'].append({
                'ConsecutivoId': facturacion.ConsecutivoId,
                'LineaId': facturacion.LineaId.LineaId,
                'Linea': facturacion.LineaId.Linea,
                'Horas': facturacion.HorasFactura,
                'Dias': facturacion.DiasFactura,
                'Mes': facturacion.MesFactura,
                'Valor': facturacion.Valor,
                'Descripcion': facturacion.Descripcion,
                'NumeroFactura': facturacion.Factura
            })

    return facturacion_info

def clientes_factura_index(request):
    clientes = models.Clientes.objects.all()
    lineas = models.Linea.objects.all()
    clientes_contratos = models.ClientesContratos.objects.all()
    facturacion_clientes = models.FacturacionClientes.objects.all()
    cliente_id = None

    facturacion_info= []

    if request.method == 'GET':
        form = FacturacionFilterForm(request.GET)

        if form.is_valid():
            # Filtrar facturación según los datos del formulario
            clientes_contratos, facturacion_clientes = filtrar_facturacion(form, clientes_contratos, facturacion_clientes)
            cliente_id = form.cleaned_data.get('ClienteId')

            # Obtener la información de facturación
            facturacion_info = obtener_info_facturacion(clientes_contratos, facturacion_clientes)

            # Filtrar las líneas según el cliente seleccionado
            if cliente_id:
                lineas = lineas.filter(clientescontratos__ClienteId=cliente_id)


    else:
        form = FacturacionFilterForm()

    # Calcular totales
    totales_facturacion = calcular_totales_facturacion(facturacion_clientes)

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
        totales['Total_Valor'] += factura.Valor or 0

    return totales