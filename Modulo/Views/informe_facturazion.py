from collections import defaultdict
from django.shortcuts import render

from Modulo.forms import FacturacionFilterForm
from Modulo.models import FacturacionClientes

def filtrar_facturazion(form,factura):
    anio = form.order_by('Anio')
    Mes = form.cleaned_data.get('Mes')
    Linea = form.cleaned_data.get('LineaId')
    Cliente = form.cleaned_data.get('ClienteId')

    print("Año:", anio, "Mes:", Mes, "Linea:", Linea, "Cliente:", Cliente)

    if anio:
        factura = factura.filter(Anio=anio)
    if Mes:
        factura = factura.filter(Mes=Mes)
    if Linea:
        factura = factura.filter(LineaId=Linea)
    if Cliente: factura = factura.filter(ClienteId=Cliente)

    return factura

#TRAE BIEN LA INFO
# Función para calcular la información de estudio del empleado
def obtener_facturazion(factura):
    factura_info = []
    lineas_info = set()  # Use a set to store unique lines

    for f in factura:   
        # Crear el diccionario con los datos del empleado y sus estudios
        datos_factura = {
            'Año': f.Anio,
            'Mes': f.Mes,
            'Linea': f.LineaId.Linea,
            'Cliente': f.ClienteId.Nombre_Cliente
        }
        
        factura_info.append(datos_factura)
        lineas_info.add(f.LineaId.Linea)  # Add unique lines to the set

    return factura_info, list(lineas_info)  # Convert set to list before returning


def facturazion_filtrada (request):
    factura_info = []  
    lineas_info = []
    show_data = False  

    if request.method == 'GET':
        #form = EmpleadoFilterForm(request.GET)
        form = FacturacionFilterForm(request.GET)

        if form.is_valid():
            # Inicializar empleados y estudios
            factura = FacturacionClientes.objects.all()
            

            # Debug: Imprimir los datos obtenidos de la base de datos
           # print("Empleados obtenidos:", empleados)
           # print("Estudios obtenidos:", estudios)

            # Obtener información de los empleados filtrada
            factura = filtrar_facturazion(form, factura)
            
            # Obtener información de los estudios de los empleados
            factura_info, lineas_info = obtener_facturazion(factura)
            show_data = bool(factura_info)  # Mostrar datos si hay resultados
            
    else: 
        #form = EmpleadoFilterForm()
        form = FacturacionFilterForm()

    context = {
        'form': form,
        'factura_info': factura_info,      
        'lineas_info': lineas_info,  # Add lineas_info to the context
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not factura_info else ""
    }

    return render(request, 'informes/informes_facturacion_index.html', context)