# Vista para listar empleados
from decimal import Decimal
import json
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from Modulo.forms import ColaboradorFilterForm
from Modulo.models import Clientes, Concepto, Consultores, Empleado, Horas_Habiles, Ind_Operat_Clientes, Ind_Operat_Conceptos, Linea, Modulo, Tiempos_Cliente, TiemposConcepto, TiemposFacturables
from django.shortcuts import render
from collections import defaultdict
from django.db import transaction
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_registro_tiempos')

def guardar_tiempos_cliente(anio, mes, documento, cliente_id, linea_id, modulo_id, horas):
    try:
        # Validar que modulo_id esté presente y sea válido
        if not modulo_id:
            raise ValidationError("El campo ModuloId es requerido.")
        if not str(modulo_id).isdigit():
            raise ValidationError("ModuloId debe ser un número entero válido.")
        
        modulo_id = int(modulo_id)  # Asegurar que es un entero
        # Verificar si existe el registro
        tiempo_cliente, creado = Tiempos_Cliente.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            Documento=documento,
            ClienteId_id=cliente_id,
            LineaId_id=linea_id,
            ModuloId_id=modulo_id,
            defaults={'Horas': horas}
        )
        if creado:
            if horas == '0':
                tiempo_cliente.delete()        
        else:
            if horas == '0':
                tiempo_cliente.delete()
            elif tiempo_cliente.Horas != horas:
                # Si el registro existe y las horas son diferentes, actualizamos las horas
                tiempo_cliente.Horas = horas
                tiempo_cliente.save()
        return tiempo_cliente
    except Exception as e:
        raise ValidationError(f"Error al guardar los tiempos del cliente: {str(e)}")

def guardar_tiempos_concepto(anio, mes, documento, concepto_id, linea_id, horas):
    try:
        # Verificar si existe el registro
        tiempo_concepto, creado = TiemposConcepto.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            Documento=documento,
            defaults={'Horas': horas},
            ConceptoId_id=concepto_id, 
            LineaId_id=linea_id
        )
        if creado:
            if horas == '0':
                tiempo_concepto.delete()
        else:
            if horas == '0':
                tiempo_concepto.delete()
            elif tiempo_concepto.Horas != horas:
                # Si el registro existe y las horas son diferentes, actualizamos las horas
                tiempo_concepto.Horas = horas
                tiempo_concepto.save()
        return tiempo_concepto
    except Exception as e:
        raise ValidationError(f"Error al guardar los tiempos del concepto: {str(e)}")

def guardar_tiempos_facturables(anio, mes, linea_id, cliente_id, horas):
    try:
        # Verificar si existe el registro
        tiempo_facturable, creado = TiemposFacturables.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            LineaId_id=linea_id,
            ClienteId_id=cliente_id,
            defaults={'Horas': horas}
        )
        if creado:
            if horas == '0':
                tiempo_facturable.delete()
        else:
            if horas == '0':
                tiempo_facturable.delete()
            elif tiempo_facturable.Horas != horas:
                # Si el registro existe y las horas son diferentes, actualizamos las horas
                tiempo_facturable.Horas = horas
                tiempo_facturable.save()
        return tiempo_facturable
    except Exception as e:
        raise ValidationError(f"Error al guardar los tiempos facturables: {str(e)}")

#Guardar totales de operación para cada linea
def guardar_totales_operacion(anio, mes, linea_id, horas_trabajadas, horas_facturables):
    try:
        # Convertir a enteros si es necesario
        anio = int(anio)
        mes = int(mes)
        linea_id = int(linea_id)
        horas_trabajadas = float(horas_trabajadas)
        horas_facturables = float(horas_facturables)

        # Obtener la instancia de Linea
        from Modulo.models import Linea
        linea = Linea.objects.get(LineaId=linea_id)

        # Crear o actualizar el registro
        total_operacion, creado = Ind_Operat_Clientes.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            LineaId=linea,
            defaults={
                'HorasTrabajadas': horas_trabajadas,
                'HorasFacturables': horas_facturables
            }
        )

        if not creado:
            total_operacion.HorasTrabajadas = horas_trabajadas
            total_operacion.HorasFacturables = horas_facturables
            total_operacion.save()

        return total_operacion

    except Exception as e:
        raise ValidationError(f"Error al guardar los totales de operación: {str(e)}")

#Guardar totales de conceptos para cada linea
def guardar_totales_concepto(anio, mes, linea_id, concepto_id, horas_concepto):
    try:
        # Convertir a enteros si es necesario
        anio = int(anio)
        mes = int(mes)
        linea_id = int(linea_id)
        concepto_id = int(concepto_id)
        horas_concepto = float(horas_concepto)

        # Obtener las instancias de Linea y Concepto
        from Modulo.models import Linea, Concepto
        linea = Linea.objects.get(LineaId=linea_id)
        concepto = Concepto.objects.get(ConceptoId=concepto_id)

        # Crear o actualizar el registro
        total_concepto, creado = Ind_Operat_Conceptos.objects.get_or_create(
            Anio=anio,
            Mes=mes,
            LineaId=linea,
            ConceptoId=concepto,
            defaults={'HorasConcepto': horas_concepto}
        )

        if not creado:
            total_concepto.HorasConcepto = horas_concepto
            total_concepto.save()

        return total_concepto

    except Exception as e:
        raise ValidationError(f"Error al guardar los totales por concepto: {str(e)}")

@transaction.atomic
def registro_tiempos_guardar(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rows = data.get('data', [])
            # Aquí puedes procesar cada fila
            for row in rows:
                # Si es un registro de cliente, concepto o facturables
                if 'Documento' in row:
                    documento = row.get('Documento')
                    anio = row.get('Anio')
                    mes = row.get('Mes')
                    linea_id = row.get('LineaId')
                    modulo_id = row.get('ModuloId')

                    if 'ClienteId' in row and 'Tiempo_Clientes' in row:
                        cliente_id = row.get('ClienteId')
                        horas = row.get('Tiempo_Clientes')
                        guardar_tiempos_cliente(anio, mes, documento, cliente_id, linea_id, modulo_id, horas)

                    elif 'ConceptoId' in row and 'Tiempo_Conceptos' in row:
                        concepto_id = row.get('ConceptoId')
                        horas = row.get('Tiempo_Conceptos')
                        guardar_tiempos_concepto(anio, mes, documento, concepto_id, linea_id, horas)

                elif 'LineaId' in row and 'Horas_Facturables' in row and 'ClienteId' in row:
                    linea_id = row.get('LineaId')
                    cliente_id = row.get('ClienteId')
                    horas = row.get('Horas_Facturables')
                    guardar_tiempos_facturables(
                        anio=row.get('Anio'),
                        mes=row.get('Mes'),
                        linea_id=linea_id, 
                        cliente_id=cliente_id, 
                        horas=horas
                    )

                # Si es un registro de tipo 'linea' o 'concepto'
                elif 'type' in row:
                    if row['type'] == 'linea':
                        guardar_totales_operacion(
                            anio=row.get('Anio'),
                            mes=row.get('Mes'),
                            linea_id=row.get('LineaId'),
                            horas_trabajadas=row.get('horasTrabajadas'),
                            horas_facturables=row.get('horasFacturables')
                        )
                    
                    elif row['type'] == 'concepto':
                        guardar_totales_concepto(
                            anio=row.get('Anio'),
                            mes=row.get('Mes'),
                            linea_id=row.get('LineaId'),
                            concepto_id=row.get('ConceptoId'),
                            horas_concepto=row.get('horas')
                        )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})
    return JsonResponse({'status': 'error', 'error': 'Método no permitido.'})


# Función para filtrar los colaboradores con los filtros especificados
def filtrar_colaboradores(form, empleados, consultores, clientes, tiempo_clientes, tiempo_conceptos):
    # No filtrar por estado activo
    empleados = empleados.order_by('Documento')
    consultores = consultores.order_by('Documento')
    

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


def filtrar_linea(form, tiempos_facturables, lineas, clientes): 
    # Ordenar por Linea
    tiempos_facturables = tiempos_facturables.order_by('LineaId')

    # Recuperar los filtros del formulario
    anio = form.cleaned_data.get('Anio')
    mes = form.cleaned_data.get('Mes')
    linea_id = form.cleaned_data.get('LineaId')
    cliente_id = form.cleaned_data.get('ClienteId')

    # Filtrar por los diferentes parámetros
    if anio:
        tiempos_facturables = tiempos_facturables.filter(Anio=anio)

    if mes:
        tiempos_facturables = tiempos_facturables.filter(Mes=mes)

    if linea_id:
        tiempos_facturables = tiempos_facturables.filter(LineaId=linea_id)

    if cliente_id:
        tiempos_facturables = tiempos_facturables.filter(ClienteId=cliente_id)

    return tiempos_facturables, lineas, clientes


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
def obtener_info_colaborador(colaborador, clientes, conceptos, tiempo_clientes, tiempo_conceptos, modulo=None):
    cliente_info = {cliente.ClienteId: cliente for cliente in clientes}
    concepto_info = {concepto.ConceptoId: concepto for concepto in conceptos}

    if modulo:
        modulo_id = modulo.ModuloId
        modulo_nombre = modulo.Modulo
    else:
        modulo_id = colaborador.ModuloId.ModuloId
        modulo_nombre = colaborador.ModuloId.Modulo

    # Obtener horas trabajadas por cliente
    horas_trabajadas_cliente = tiempo_clientes.filter(Documento=colaborador.Documento, ModuloId=modulo_id)
    clientes_colaborador = {cliente.ClienteId: 0 for cliente in clientes}

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

    # Verificar si el colaborador tiene horas registradas
    tiene_horas_registradas = total_horas_trabajadas > 0

    # Solo agregar al colaborador si está activo o tiene horas registradas
    if colaborador.Activo if isinstance(colaborador, Empleado) else colaborador.Estado or tiene_horas_registradas:
        # Crear un diccionario con la información del colaborador
        colaborador_info = {
            'Nombre': colaborador.Nombre,
            'Documento': colaborador.Documento,
            'Linea': colaborador.LineaId.Linea,
            'LineaId': colaborador.LineaId.LineaId,     
            'Perfil': colaborador.PerfilId.Perfil,
            'ModuloId': modulo_id,
            'Modulo': modulo_nombre,
            'Empresa': "Flag Soluciones" if isinstance(colaborador, Empleado) else colaborador.Empresa,
            'Clientes': {cliente_id: {'Cliente': cliente_info[cliente_id].Nombre_Cliente, 'ClienteId': cliente_id, 'tiempo_clientes': horas} for cliente_id, horas in clientes_colaborador.items()},
            'Total_Clientes': total_horas_clientes,
            'Conceptos': {concepto_id: {'Concepto': concepto_info[concepto_id].Descripcion, 'ConceptoId': concepto_id, 'tiempo_conceptos': horas} for concepto_id, horas in conceptos_colaborador.items()},
            'Total_Conceptos': total_horas_conceptos,
            'Total_Horas': total_horas_trabajadas,  
            'Activo': colaborador.Activo if isinstance(colaborador, Empleado) else colaborador.Estado  # Incluir estado activo
        }

        return colaborador_info
    return None


def obtener_info_linea(linea, clientes, tiempo_facturables):
    cliente_info = {cliente.ClienteId: cliente for cliente in clientes}

    # Obtener horas facturables por cliente
    horas_facturables_cliente = tiempo_facturables.filter(LineaId=linea)
    clientes_linea = {cliente.ClienteId: 0 for cliente in clientes}  # Inicializamos las horas con 0
    for tiempo_facturable in horas_facturables_cliente:
        if tiempo_facturable.ClienteId_id in clientes_linea:
            clientes_linea[tiempo_facturable.ClienteId_id] += tiempo_facturable.Horas

    # Calcular el total de horas facturables por todos los clientes
    total_horas_facturables = sum(clientes_linea.values())

    # Crear un diccionario con la información de la línea
    linea_info = {
        'Linea': linea.Linea,
        'LineaId': linea.LineaId,  # Incluir LineaId
        'Clientes': {cliente_id: {'Cliente': cliente_info[cliente_id].Nombre_Cliente, 'ClienteId': cliente_id, 'horas_facturables': horas} for cliente_id, horas in clientes_linea.items()},
        'Total_Horas_Facturables': total_horas_facturables
    }

    return linea_info


# Vista para mostrar la información filtrada de los colaboradores
def registro_tiempos_index(request):
    empleados = Empleado.objects.select_related('LineaId', 'PerfilId', 'ModuloId').all().order_by('Nombre')
    consultores = Consultores.objects.select_related('LineaId', 'PerfilId', 'ModuloId').all().order_by('Nombre')
    clientes = Clientes.objects.all().order_by('Nombre_Cliente')
    conceptos = Concepto.objects.all()
    tiempo_clientes = Tiempos_Cliente.objects.select_related('ClienteId').all()
    tiempo_conceptos = TiemposConcepto.objects.select_related('ConceptoId').all()
    horas_facturables = TiemposFacturables.objects.select_related('LineaId', 'ClienteId').all()
    lineas = Linea.objects.all()

    colaborador_info = []
    lineas_info = []
    show_data = False  

    if request.method == 'GET':
        form = ColaboradorFilterForm(request.GET)

        if form.is_valid():
            # Filtrar colaboradores según los datos del formulario
            empleados, consultores, tiempo_clientes, tiempo_conceptos = filtrar_colaboradores(form, empleados, consultores, clientes, tiempo_clientes, tiempo_conceptos)

            # Obtener información de los colaboradores
            for empleado in empleados:
                info = obtener_info_colaborador(empleado, clientes, conceptos, tiempo_clientes, tiempo_conceptos)

                if info:  # Solo agregar si el colaborador tiene horas registradas o está activo
                    colaborador_info.append(info)

            # Procesar consultores con módulos de Tarifa_Consultores O Tiempos_Cliente
            for consultor in consultores:
                # Obtener módulos únicos de ambas fuentes
                modulos_tarifa = Modulo.objects.filter(
                    tarifa_consultores__documentoId=consultor.Documento
                ).distinct()
                
                modulos_tiempos = Modulo.objects.filter(
                    tiempos_cliente__Documento=consultor.Documento
                ).distinct()
                
                # Combinar ambos querysets y eliminar duplicados
                modulos = (modulos_tarifa | modulos_tiempos).distinct()

                if modulos.exists():
                    for modulo in modulos:
                        info = obtener_info_colaborador(consultor, clientes, conceptos, tiempo_clientes, tiempo_conceptos, modulo)
                        if info:
                            colaborador_info.append(info)
                else:
                    # Usar módulo por defecto solo si no hay registros
                    info = obtener_info_colaborador(consultor, clientes, conceptos, tiempo_clientes, tiempo_conceptos)
                    if info:
                        colaborador_info.append(info)

            
            # Ordenar colaboradores alfabéticamente por nombre
            colaborador_info =sorted(colaborador_info, key=lambda x: ( x.get('Nombre', ''),     x.get('Empresa', '')))

            show_data = bool(colaborador_info)  # Mostrar datos si hay resultados

            # Extraer líneas únicas de colaborador_info
            lineas_unicas = list({colaborador['Linea'] for colaborador in colaborador_info})

            # Filtrar líneas y clientes según los datos del formulario
            tiempos_facturables, lineas, clientes = filtrar_linea(form, horas_facturables, lineas, clientes)

            # Obtener información de las líneas
            for linea in lineas:
                if linea.Linea in lineas_unicas:
                    lineas_info.append(obtener_info_linea(linea, clientes, tiempos_facturables))
                    

    else: 
        form = ColaboradorFilterForm()

    # Calcular totales
    totales, totales_facturables = calcular_totales(colaborador_info, lineas_info)

    context = {
        'form': form,
        'colaborador_info': colaborador_info,
        'Clientes': clientes.values_list('Nombre_Cliente', flat=True),
        'Conceptos': conceptos.values_list('Descripcion', flat=True),
        'Totales': totales, 
        'TotalesFacturables': totales_facturables,
        'Horas_Facturables': horas_facturables,
        'Tiempo_Lineas': lineas_info,
        'show_data': show_data,
        'mensaje': "No se encontraron resultados para los filtros aplicados." if not colaborador_info else ""
    }

    return render(request, 'Registro_Tiempos/registro_tiempos_index.html', context)

def calcular_totales(colaborador_info, lineas_info):
    # Usar Decimal como tipo base para los totales
    totales = defaultdict(Decimal)
    totales_facturables = defaultdict(Decimal)
    
    # Sumar horas clientes y conceptos
    for empleado in colaborador_info:
        for cliente in empleado['Clientes'].values():
            tiempo = Decimal(str(cliente['tiempo_clientes']))
            totales[cliente['ClienteId']] += tiempo
        
        for concepto in empleado['Conceptos'].values():
            tiempo = Decimal(str(concepto['tiempo_conceptos']))
            totales[concepto['ConceptoId']] += tiempo
    
    # Calcular totales generales
    totales['Total_Clientes'] = sum(
        Decimal(str(empleado['Total_Clientes'])) 
        for empleado in colaborador_info
    )
    
    totales['Total_Conceptos'] = sum(
        Decimal(str(empleado['Total_Conceptos'])) 
        for empleado in colaborador_info
    )
    
    totales['Total_Horas'] = sum(
        Decimal(str(empleado['Total_Horas'])) 
        for empleado in colaborador_info
    )

    # Horas facturables
    for linea in lineas_info:
        for cliente in linea['Clientes'].values():
            horas = Decimal(str(cliente['horas_facturables']))
            totales_facturables[cliente['ClienteId']] += horas
    
    totales_facturables['Total_Clientes'] = sum(
        Decimal(str(linea['Total_Horas_Facturables'])) 
        for linea in lineas_info
    )
    
    totales_facturables['Total_Horas'] = sum(
        Decimal(str(linea['Total_Horas_Facturables'])) 
        for linea in lineas_info
    )
    
    return totales, totales_facturables


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

def calcular_totales_por_linea(datos):
    # Estructuras para almacenar los totales
    totales_operacion = defaultdict(float)  # {linea: total_horas_trabajadas}
    totales_facturables = defaultdict(float)  # {linea: total_horas_facturables}
    totales_conceptos = defaultdict(lambda: defaultdict(float))  # {linea: {concepto: total_horas}}

    for fila in datos:
        linea = fila['Línea']
        total_operacion = float(fila['Total Operación'])
        horas_facturables = float(fila.get('Horas Facturables', 0))

        # Sumar horas trabajadas y facturables por línea
        totales_operacion[linea] += total_operacion
        totales_facturables[linea] += horas_facturables

        # Sumar horas por concepto
        for concepto, horas in fila.items():
            if concepto in ['Líder', 'Capacitaciones', 'Día Familia', 'Vacaciones', 'Calamidad', 'Preventa', 'Otros']:
                totales_conceptos[linea][concepto] += float(horas)

    return totales_operacion, totales_facturables, totales_conceptos
