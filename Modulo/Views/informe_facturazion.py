from collections import defaultdict
from django.shortcuts import render

from Modulo.forms import FacturacionFilterForm
from Modulo.models import FacturacionClientes

def filtrar_facturazion(form,factura):
    Año = factura.order_by('Anio')
    Mes = form.cleaned_data.get('Mes')
    Linea = form.cleaned_data.get('LineaId')
    Cliente = form.cleaned_data.get('Cargo')

    if Año:
        factura = factura.filter(Anio=Año)
    if Mes:
        factura = factura.filter(Mes=Mes)
    if Linea:
        factura = factura.filter(LineaId=Linea)
    if Cliente: factura = factura.filter(ClienteId=Cliente)

    return factura

#TRAE BIEN LA INFO
# Función para calcular la información de estudio del empleado
def obtener_facturazion(facturas):
    factura_info = []

    # Organizar los estudios por documentoId para optimizar consultas

    for factura in facturas:   
        # Crear el diccionario con los datos del empleado y sus estudios
        datos_empleado = {
            'nombre_linea': empleado.LineaId.Linea,
            'documento_colaborador': empleado.Documento,
            'nombre_colaborador': empleado.Nombre,
            'cargo': empleado.CargoId.Cargo,
            'perfil': empleado.PerfilId.Perfil,
            'modulo': empleado.ModuloId.Modulo,
        }
        
        factura_info.append(datos_empleado)

    return factura_info


def facturazion_filtrada (request):
    factura_info = []  
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
            facturazion_info = obtener_facturazion(factura)
            show_data = bool(factura_info)  # Mostrar datos si hay resultados

             # Debug: Imprimir la información de estudios de empleados
            #print("Información de estudios de empleados:", empleado_estudio_info)

    else: 
        #form = EmpleadoFilterForm()
        form = FacturacionClientes()

    context = {
        'form': form,
        'empleado_estudio_info': facturazion_info,      
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not factura_info else ""
    }

    return render(request, 'informes/informes_facturazion_index.html', context)