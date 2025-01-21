# Vista para listar empleados
import json
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from Modulo.forms import ColaboradorFilterForm
from Modulo.models import Clientes, Concepto, Consultores, Empleado, Horas_Habiles, Tiempos_Cliente, TiemposConcepto
from django.shortcuts import render
from collections import defaultdict
from django.db import transaction

def guardar_tiempos_cliente(anio, mes, documento, cliente_id, horas):
    try:
        # Verificar si existe el registro
        tiempo_cliente, creado = Tiempos_Cliente.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            Documento=documento,
            defaults={'Horas': horas},
            ClienteId_id=cliente_id  # Usar `_id` para asignar directamente el ID de la relación
        )
        if not creado and tiempo_cliente.Horas != tiempo_cliente:
            # Si el registro existe, actualizamos las horas
            tiempo_cliente.Horas = horas
            tiempo_cliente.save()
        return tiempo_cliente
    except Exception as e:
        raise ValidationError(f"Error al guardar los tiempos del cliente: {str(e)}")


def guardar_tiempos_concepto(anio, mes, documento, concepto_id, horas):
    try:
        # Verificar si existe el registro
        tiempo_concepto, creado = TiemposConcepto.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            Documento=documento,
            defaults={'Horas': horas},
            ConceptoId_id=concepto_id  # Usar `_id` para asignar directamente el ID de la relación
        )
        if not creado and tiempo_concepto.Horas != tiempo_concepto:
            # Si el registro existe, actualizamos las horas
            tiempo_concepto.Horas = horas
            tiempo_concepto.save()
        return tiempo_concepto
    except Exception as e:
        raise ValidationError(f"Error al guardar los tiempos del concepto: {str(e)}")


@transaction.atomic
def registro_tiempos_guardar(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rows = data.get('data', [])
            # Aquí puedes procesar cada fila
            for row in rows:
                documento = row.get('Documento')
                anio = row.get('Anio')
                mes = row.get('Mes')
                if 'ClienteId' in row:
                    cliente_id = row.get('ClienteId')
                    horas = row.get('Tiempo_Clientes')
                    guardar_tiempos_cliente(anio, mes, documento, cliente_id, horas)
                elif 'ConceptoId' in row:
                    concepto_id = row.get('ConceptoId')
                    horas = row.get('Tiempo_Conceptos')
                    guardar_tiempos_concepto(anio, mes, documento, concepto_id, horas)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})
    return JsonResponse({'status': 'error', 'error': 'Método no permitido.'})


# Función para filtrar los colaboradores con los filtros especificados
def filtrar_colaboradores(form, empleados, consultores, clientes, tiempo_clientes, tiempo_conceptos):
    empleados = empleados.order_by('Documento')  # Orden descendente por Documento (ajustar si otro campo es clave)
    consultores = consultores.order_by('Documento')  # Orden descendente por Documento

    # Recuperar los filtros del formulario
    anio = form.cleaned_data.get('Anio')
    mes = form.cleaned_data.get('Mes')
    linea = form.cleaned_data.get('LineaId')
    empleado = form.cleaned_data.get('Empleado')
    consultor = form.cleaned_data.get('Consultor')
    cliente = form.cleaned_data.get('ClienteId')


    # Filtrar por los diferentes parámetros
    if anio:
        tiempo_clientes = tiempo_clientes.filter(Anio=anio)
        tiempo_conceptos = tiempo_conceptos.filter(Anio=anio)

    if mes:
        tiempo_clientes = tiempo_clientes.filter(Mes=mes)
        tiempo_conceptos = tiempo_conceptos.filter(Mes=mes)

    if linea:
        empleados = empleados.filter(LineaId=linea)
        consultores = consultores.filter(LineaId=linea)

    if empleado:
        empleados = empleados.filter(Documento=empleado)

    if consultor:
        consultores = consultores.filter(Documento=consultor)

    if cliente:
        tiempo_clientes = tiempo_clientes.filter(ClienteId=cliente)

    return empleados, consultores, tiempo_clientes, tiempo_conceptos


# Función para calcular la información de los colaboradores (empleados y consultores)
def obtener_colaborador_info(empleados, consultores, clientes, conceptos, tiempo_clientes, tiempo_conceptos):
    colaborador_info = []

    # Obtener la información de los empleados
    for empleado in empleados:
        colaborador_info.append(obtener_info_colaborador(empleado, clientes, conceptos, tiempo_clientes, tiempo_conceptos))

    # Obtener la información de los consultores
    for consultor in consultores:
        colaborador_info.append(obtener_info_colaborador(consultor, clientes, conceptos, tiempo_clientes, tiempo_conceptos))

    return colaborador_info


# Función para obtener la información de un colaborador (empleado o consultor)
def obtener_info_colaborador(colaborador, clientes, conceptos, tiempo_clientes, tiempo_conceptos):
    cliente_info = {cliente.ClienteId: cliente for cliente in clientes}
    concepto_info = {concepto.ConceptoId: concepto for concepto in conceptos}

    # Obtener horas trabajadas por cliente
    horas_trabajadas_cliente = tiempo_clientes.filter(Documento=colaborador.Documento)
    clientes_colaborador = {cliente.ClienteId: 0 for cliente in clientes}  # Inicializamos las horas con 0
    for tiempo_cliente in horas_trabajadas_cliente:
        if tiempo_cliente.ClienteId_id in clientes_colaborador:
            clientes_colaborador[tiempo_cliente.ClienteId_id] += tiempo_cliente.Horas

    # Calcular el total de horas trabajadas por todos los clientes
    total_horas_clientes = sum(clientes_colaborador.values())

    # Obtener horas trabajadas por concepto
    horas_trabajadas_concepto = tiempo_conceptos.filter(Documento=colaborador.Documento)
    conceptos_colaborador = {concepto.ConceptoId: 0 for concepto in conceptos}  # Inicializamos las horas con 0
    for tiempo_concepto in horas_trabajadas_concepto:
        if tiempo_concepto.ConceptoId_id in conceptos_colaborador:
            conceptos_colaborador[tiempo_concepto.ConceptoId_id] += tiempo_concepto.Horas

    # Calcular el total de horas trabajadas por todos los conceptos
    total_horas_conceptos = sum(conceptos_colaborador.values())

    # Calcular total de horas trabajadas (puede coincidir con total_horas_clientes o total_horas_conceptos)
    total_horas_trabajadas = total_horas_clientes+total_horas_conceptos


    # Crear un diccionario con la información del colaborador
    colaborador_info = {
        'Nombre': colaborador.Nombre,
        'Documento': colaborador.Documento,
        'Linea': colaborador.LineaId.Linea,
        'Perfil': colaborador.PerfilId.Perfil,
        'Modulo': colaborador.ModuloId.Modulo,
        'Empresa': "Flag Soluciones" if isinstance(colaborador, Empleado) else colaborador.Empresa,
        'Clientes': {cliente_id: {'Cliente': cliente_info[cliente_id].Nombre_Cliente, 'ClienteId': cliente_id, 'tiempo_clientes': horas} for cliente_id, horas in clientes_colaborador.items()},
        'Total_Clientes': total_horas_clientes,
        'Conceptos': {concepto_id: {'Concepto': concepto_info[concepto_id].Descripcion, 'ConceptoId': concepto_id, 'tiempo_conceptos': horas} for concepto_id, horas in conceptos_colaborador.items()},
        'Total_Conceptos': total_horas_conceptos,
        'Total_Horas': total_horas_trabajadas
    }

    return colaborador_info


# Vista para mostrar la información filtrada de los colaboradores
def registro_tiempos_index(request):
    empleados = Empleado.objects.all()
    consultores = Consultores.objects.all()
    clientes = Clientes.objects.all()
    conceptos = Concepto.objects.all()
    tiempo_clientes = Tiempos_Cliente.objects.all()
    tiempo_conceptos = TiemposConcepto.objects.all()


    colaborador_info = []
    show_data = False  

    if request.method == 'GET':
        form = ColaboradorFilterForm(request.GET)

        if form.is_valid():
            # Filtrar colaboradores según los datos del formulario
            empleados, consultores, tiempo_clientes, tiempo_conceptos = filtrar_colaboradores(form, empleados, consultores, clientes, tiempo_clientes, tiempo_conceptos)
            
            # Obtener información de los colaboradores
            colaborador_info = obtener_colaborador_info(empleados, consultores, clientes, conceptos, tiempo_clientes, tiempo_conceptos)
            show_data = bool(colaborador_info)  # Mostrar datos si hay resultados

    else: 
        form = ColaboradorFilterForm()

    # Calcular totales
    totales = calcular_totales(colaborador_info)


    context = {
        'form': form,
        'colaborador_info': colaborador_info,
        'Clientes': clientes.values_list('Nombre_Cliente', flat=True),
        'Conceptos': conceptos.values_list('Descripcion', flat=True),
        'Totales': totales, 
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not colaborador_info else ""
    }

    return render(request, 'Registro_Tiempos/registro_tiempos_index.html', context)


def calcular_totales(colaborador_info):
    totales = defaultdict(int)
    
    # Sumar las horas por cada columna (clientes y conceptos)
    for empleado in colaborador_info:
        for cliente in empleado['Clientes'].values():
            totales[cliente['ClienteId']] += cliente['tiempo_clientes']
        
        for concepto in empleado['Conceptos'].values():
            totales[concepto['ConceptoId']] += concepto['tiempo_conceptos']
    
    # Calcular los totales generales
    totales['Total_Clientes'] = sum(empleado['Total_Clientes'] for empleado in colaborador_info)
    totales['Total_Conceptos'] = sum(empleado['Total_Conceptos'] for empleado in colaborador_info)
    totales['Total_Horas'] = sum(empleado['Total_Horas'] for empleado in colaborador_info)
    return totales


def obtener_horas_habiles(anio, mes):
    try:
        horas_habiles = Horas_Habiles.objects.get(Anio=anio, Mes=mes)
        return horas_habiles.Dias_Habiles, horas_habiles.Horas_Laborales
    except Horas_Habiles.DoesNotExist:
        return None, None
    

def obtener_horas_habiles_view(request):
    anio = request.GET.get('anio')
    mes = request.GET.get('mes')
    dias_habiles, horas_laborales = obtener_horas_habiles(anio, mes)
    return JsonResponse({'Dias_Habiles': dias_habiles, 'Horas_Laborales': horas_laborales})