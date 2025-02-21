from collections import defaultdict
from django.shortcuts import render
from Modulo.forms import FacturacionFilterForm
from Modulo.models import FacturacionClientes

def filtrar_facturazion(form, factura):
    anio = form.cleaned_data.get('Anio')
    Linea = form.cleaned_data.get('LineaId')
    Cliente = form.cleaned_data.get('ClienteId')

    if anio:
        factura = factura.filter(Anio=anio)
    if Linea:
        factura = factura.filter(LineaId=Linea)
    if Cliente: 
        factura = factura.filter(ClienteId=Cliente)
    
    return factura

# Función para calcular el total de los valores por Mes
def obtener_Totales(Meses_info, factura):
    totales = []
    for mes in Meses_info:
        total_mes = sum(f.Valor or 0 for f in factura if f.Mes == mes)  # Maneja valores None
        totales.append(total_mes)
    return totales

# Función para calcular la información de facturación
def obtener_facturazion(factura):
    factura_info = []
    lineas_info = set()  # Usamos un set para evitar duplicados
    Meses_info = set()

    for f in factura:   
        datos_factura = {
            'Valor': f.Valor,
            'Cliente':f.ClienteId
        }
        factura_info.append(datos_factura)
        lineas_info.add(f.LineaId.Linea)  # Almacenar líneas únicas
        Meses_info.add(f.Mes)

    return factura_info, list(lineas_info), list(Meses_info)  # Convertir sets a listas

def facturazion_filtrada(request):
    factura_info = []
    lineas_info = []
    Meses_info = []
    Total_Meses = []
    show_data = False

    if request.method == 'GET':
        form = FacturacionFilterForm(request.GET)
        if form.is_valid():
            factura = FacturacionClientes.objects.all()
            factura = filtrar_facturazion(form, factura)
            factura_info, lineas_info, Meses_info = obtener_facturazion(factura)
            Total_Meses = obtener_Totales(Meses_info, factura)
            show_data = bool(factura_info)

            # Convertimos en lista de tuplas
            Meses_info = list(zip(Meses_info, Total_Meses))

    else:
        form = FacturacionFilterForm()

    context = {
        'form': form,
        'factura_info': factura_info,
        'lineas_info': lineas_info,
        'Meses_info': Meses_info,  # Ahora es una lista de tuplas [(mes, total_mes)]
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not factura_info else ""
    }

    print("este es el cliente",factura_info)

    print("esto es lo que trae Meses_info:", Meses_info)  # Ahora verás [(1, 2.0)]

    return render(request, 'informes/informes_facturacion_index.html', context)
