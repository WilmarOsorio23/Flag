from ctypes import alignment
from datetime import datetime, date
import io
import json
from django import template
from django.core.cache import cache
# from tkinter.font import Font # Eliminada ya que no es necesaria para la web
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect, render
from openpyxl import Workbook
from Modulo.forms import PagareFilterForm
from Modulo.models import Empleado, PagarePlaneado, PagareEjecutado, TipoPagare
from django.shortcuts import render, get_object_or_404
from Modulo.models import Pagare, ActividadPagare, PagarePlaneado # type: ignore
from openpyxl.styles import Border, Side, Font, PatternFill, Alignment
from dateutil.parser import parse as parse_date
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction  # Ensure this import is present for transaction.atomic


def pagare_index(request):
    form = PagareFilterForm(request.GET or None)
    empleados = []
    actividades = ActividadPagare.objects.all()
    pagare_ejecutado = PagareEjecutado.objects.all()
    tipos_pagare = TipoPagare.objects.all()

    pagares = Pagare.objects.select_related('Tipo_Pagare').all()
    datos_para_exportar = []  # Inicializa la lista
    response = HttpResponse() # Inicializa response

    
    
    if form.is_valid():
        documentos = form.cleaned_data.get('documento')
        if documentos:
            empleados = Empleado.objects.filter(Activo=True, Documento__in=documentos).select_related('LineaId', 'CargoId')
            
            

    return render(request, 'Pagare/Pagare_index.html', {
        'form': form,
        'empleados': empleados,
        'actividades': actividades,
        'pagare_ejecutado': pagare_ejecutado,
        'datos_para_exportar': datos_para_exportar,  # Pasa los datos a la plantilla
        'tipos_pagare': tipos_pagare,
        'pagares': pagares,
        
    })



@csrf_exempt
def eliminar_pagares(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids_a_eliminar = data.get('ids', [])

            if not ids_a_eliminar:
                return JsonResponse({'success': False, 'message': 'No se recibieron pagarés para eliminar.'})

            # Eliminar los pagarés por ID
            Pagare.objects.filter(Pagare_Id__in=ids_a_eliminar).delete()

            return JsonResponse({'success': True, 'message': 'Pagarés eliminados correctamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
@csrf_exempt
def actualizar_pagare(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("✅ Datos recibidos:", data)

            for doc, valores in data.items():
                try:
                    pagare_id = valores.get('pagare_id')
                    pagare = Pagare.objects.get(pk=pagare_id)

                    # Actualizar campos principales del pagaré
                    pagare.Fecha_Creacion_Pagare = valores['fecha_creacion']
                    pagare.Tipo_Pagare_id = valores['tipo_pagare']
                    pagare.descripcion = valores.get('descripcion', pagare.descripcion)
                    pagare.Fecha_inicio_Condonacion = valores.get('fecha_inicio') or None

                    # Si la fecha inicio está vacía o deshabilitada, reiniciar fecha fin
                    if not pagare.Fecha_inicio_Condonacion:
                        pagare.Fecha_fin_Condonacion = None
                    else:
                        pagare.Fecha_fin_Condonacion = valores.get('fecha_fin') or None

                    pagare.Meses_de_condonacion = valores['meses_condonacion']
                    
                    # Validar y actualizar el valor del pagaré solo si ha sido modificado
                    nuevo_valor_pagare = limpiar_float(valores['valor_pagare'])
                    if nuevo_valor_pagare != pagare.Valor_Pagare:
                        pagare.Valor_Pagare = nuevo_valor_pagare

                    pagare.porcentaje_ejecucion = float(valores['ejecucion'])
                    pagare.Valor_Capacitacion = limpiar_float(valores.get('valor_capacitacion'))
                    pagare.estado = valores['estado']
                    pagare.save()
                    print("✅ Pagaré actualizado correctamente.")

                    # Procesar actividades ejecutadas
                    actividades_recibidas = valores.get('ejecutadas', [])
                    recibidas_ids = [int(a['actividad_id']) for a in actividades_recibidas]
                    
                    # Crear lista de IDs recibidos
                    actividad_ids_recibidos = []
                    
                    for act in actividades_recibidas:
                        actividad_id = int(act['actividad_id'])
                        PagareEjecutado.objects.update_or_create(
                            Pagare=pagare,
                            Actividad_id=actividad_id,
                            defaults={'Horas_Ejecutadas': int(act['horas'])}
                        )
                        print(f"✓ Actividad {actividad_id} actualizada")

                    # 2. Eliminar solo las que no están en el request
                    actividades_a_eliminar = PagareEjecutado.objects.filter(
                        Pagare=pagare
                    ).exclude(Actividad_id__in=recibidas_ids)
                    
                    if actividades_a_eliminar.exists():
                        print(f"🗑️ Eliminando {actividades_a_eliminar.count()} actividades")
                        actividades_a_eliminar.delete()

                except Exception as e:
                    print(f"❌ Error en documento {doc}: {str(e)}")
                    continue

            return JsonResponse({'mensaje': 'Actualización exitosa'}, status=200)

        except Exception as e:
            print("❌ Error general:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def limpiar_float(valor_str):
    if valor_str is None:
        return 0.0
    # Si el valor ya es un número sin formato, convertirlo directamente
    try:
        return float(valor_str)
    except ValueError:
        # Limpiar solo si contiene caracteres no numéricos
        return float(
            valor_str.replace('$', '')
                    .replace('\xa0', '')
                    .replace('.', '')
                    .replace(',', '.')
        )

@csrf_exempt
def obtener_datos_pagares(request):
    print("Solicitud recibida")
    try:
        if request.method == 'POST':
            print("Datos recibidos:", request.body)
            data = json.loads(request.body)
            ids = list(map(int, data.get('pagare_ids', [])))

            print("IDs solicitados:", ids)

            pagarés = Pagare.objects.select_related('Tipo_Pagare').filter(Pagare_Id__in=ids)
            ejecutados = PagareEjecutado.objects.select_related('Actividad').filter(Pagare__Pagare_Id__in=ids)

            print("Pagarés encontrados:", pagarés.count()) 

            pagares_data = []
            for pagare in pagarés:
                # Calcular el valor de capacitación otorgado
                valor_capacitacion_otorgado = 0
                if pagare.Valor_Pagare and pagare.porcentaje_ejecucion:
                    valor_capacitacion_otorgado = (float(pagare.Valor_Pagare) * float(pagare.porcentaje_ejecucion)) / 100

                pagares_data.append({
                    'id': pagare.Pagare_Id,
                    'documento': pagare.Documento,
                    'fecha_creacion': pagare.Fecha_Creacion_Pagare.strftime('%Y-%m-%d'),
                    'tipo_pagare': {
                        'id': pagare.Tipo_Pagare.Tipo_PagareId,
                        'descripcion': pagare.Tipo_Pagare.Desc_Tipo_Pagare,
                    },
                    'descripcion': pagare.descripcion,
                    'fecha_inicio': pagare.Fecha_inicio_Condonacion.strftime('%Y-%m-%d') if pagare.Fecha_inicio_Condonacion else None,
                    'fecha_fin': pagare.Fecha_fin_Condonacion.strftime('%Y-%m-%d') if pagare.Fecha_fin_Condonacion else None,
                    'meses_condonacion': pagare.Meses_de_condonacion,
                    'valor_pagare': str(pagare.Valor_Pagare),
                    'ejecucion': round(pagare.porcentaje_ejecucion, 2) if pagare.porcentaje_ejecucion is not None else 0,   
                    'valor_capacitacion': round(valor_capacitacion_otorgado, 2),
                    'estado': pagare.estado,
                })
            # En obtener_datos_pagares, verifica que el Tipo_PagareId=3 exista:
            print("Tipos de pagaré enviados:", [tipo.Tipo_PagareId for tipo in TipoPagare.objects.all()])

            planeados = PagarePlaneado.objects.select_related('Actividad').filter(Pagare__Pagare_Id__in=ids)
            planeados_data = [{
                'pagare_id': p.Pagare.Pagare_Id,
                'actividad_id': p.Actividad.Act_PagareId,  # Campo correcto
                'actividad_nombre': p.Actividad.Descripcion_Act,  # Nombre explícito
                'horas_planeadas': p.Horas_Planeadas
            } for p in PagarePlaneado.objects.filter(Pagare__Pagare_Id__in=ids)]

            ejecutados = PagareEjecutado.objects.select_related('Actividad').filter(Pagare__Pagare_Id__in=ids)
            ejecutados_data = [{
                'pagare_id': e.Pagare.Pagare_Id,
                'actividad_id': e.Actividad.Act_PagareId,
                'actividad_nombre': e.Actividad.Descripcion_Act,
                'horas_ejecutadas': e.Horas_Ejecutadas
            } for e in ejecutados]


            return JsonResponse({
                'pagares': pagares_data,
                'planeadas': planeados_data,
                'ejecutadas': ejecutados_data
            })

        return JsonResponse({'error': str(e)}, status=405)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print("Error en la vista:", str(e))  # Esto imprime el error en tu terminal
        return JsonResponse({'error': str(e)}, status=500)


    
def pagares_exitoso(request):
    return render(request, 'pagares_exitoso.html')



register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")

    

def obtener_pagares_empleado(request):
    documentos = request.GET.getlist('documentos[]')
    pagares = Pagare.objects.filter(Documento__in=documentos).select_related('Tipo_Pagare').values(
        'Pagare_Id',
        'Tipo_Pagare__Nombre_Tipo_Pagare',
        'Fecha_Creacion_Pagare',
        'estado'
    )
    return JsonResponse(list(pagares), safe=False)


def pag_planeado(request, pagare_id):
    pagare = get_object_or_404(Pagare, pk=pagare_id)
    todas_actividades = ActividadPagare.objects.all()
    
    if request.method == 'POST':
        # Procesar actividades seleccionadas
        for key in request.POST:
            if key.startswith('horas_planeadas_'):
                actividad_id = key.split('_')[-1]
                horas = request.POST.get(key, 0)
                actividad = get_object_or_404(ActividadPagare, pk=actividad_id)
                PagarePlaneado.objects.update_or_create(
                    Pagare=pagare,
                    Actividad=actividad,
                    defaults={'Horas_Planeadas': horas}
                )
        return redirect('pag_planeado', pagare_id=pagare_id)

    return render(request, 'Pagare/Pag_Planeado.html', {
        'pagare': pagare,
        'todas_actividades': todas_actividades,
    })

def agregar_actividad_planeada(request, pagare_id):
    if request.method == 'POST':
        actividad_id = request.POST.get('actividad_id')
        horas_planeadas = request.POST.get('horas_planeadas', 0)

        pagare = get_object_or_404(Pagare, pk=pagare_id)
        actividad = get_object_or_404(ActividadPagare, pk=actividad_id)

        # Evitar duplicados
        PagarePlaneado.objects.get_or_create(
            Pagare=pagare,
            Actividad=actividad,
            defaults={'Horas_Planeadas': horas_planeadas}
        )

    return redirect('pag_planeado', pagare_id=pagare_id)

def pag_ejecutado(request, pagare_id):
    pagare = get_object_or_404(Pagare, pk=pagare_id)
    todas_actividades = ActividadPagare.objects.all()

    if request.method == 'POST':
        # Procesar las horas ejecutadas enviadas por el formulario
        for key in request.POST:
            if key.startswith('horas_ejecutadas_'):
                actividad_id = key.split('_')[-1]
                horas = request.POST.get(key, 0)
                
                print(f"Actividad: {actividad_id}, Horas: {horas}")
                actividad = get_object_or_404(ActividadPagare, pk=actividad_id)
                
                # Crear o actualizar registro ejecutado
                PagareEjecutado.objects.update_or_create(
                    Pagare=pagare,
                    Actividad=actividad,
                    defaults={'Horas_Ejecutadas': horas}
                )
        return redirect('pag_ejecutado', pagare_id=pagare_id)

    # Obtener registros ejecutados existentes para precargar en el formulario
    ejecutados = PagareEjecutado.objects.filter(Pagare=pagare)

    return render(request, 'Pagare/Pag_Ejecutado.html', {
        'pagare': pagare,
        'todas_actividades': todas_actividades,
        'ejecutados': ejecutados,
    })


def agregar_actividad_ejecutada(request, pagare_id):
    if request.method == 'POST':
        actividad_id = request.POST.get('actividad_id')
        horas_ejecutadas = request.POST.get('horas_ejecutadas', 0)

        pagare = get_object_or_404(Pagare, pk=pagare_id)
        actividad = get_object_or_404(ActividadPagare, pk=actividad_id)

        # Evitar duplicados
        PagareEjecutado.objects.get_or_create(
            Pagare=pagare,
            Actividad=actividad,
            defaults={'Horas_Ejecutadas': horas_ejecutadas}
        )

    return redirect('pag_ejecutado', pagare_id=pagare_id)



@csrf_exempt
def guardar_pagare(request):
    if request.method == 'POST':
        try:
            # Versión para AJAX (JSON)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                print("\nDatos JSON recibidos:")
                print(json.dumps(data, indent=4, ensure_ascii=False))
                
                for pagare_data in data:
                    ejecucion = pagare_data['general'].get('ejecucion', None)
                    if ejecucion:
                        try:
                            ejecucion = float(ejecucion.replace('%', '').strip())  # Eliminar el símbolo '%' y convertir a float
                        except ValueError:
                            ejecucion = None  
                    # Crear/Actualizar Pagare principal
                    pagare = Pagare.objects.create(
                        Documento=pagare_data['documento'],
                        Fecha_Creacion_Pagare=pagare_data['general']['fecha_creacion'],
                        Tipo_Pagare_id=pagare_data['general']['tipo_pagare'],
                        descripcion=pagare_data['general'].get('descripcion', 'Sin descripción'),
                        Fecha_inicio_Condonacion=pagare_data['general']['fecha_inicio'],
                        Fecha_fin_Condonacion=pagare_data['general']['fecha_fin'],
                        Meses_de_condonacion=pagare_data['general']['meses_condonacion'],
                        Valor_Pagare=pagare_data['general']['valor_pagare'],
                        porcentaje_ejecucion=ejecucion,
                        estado=pagare_data['general']['estado']
                    )


                    # Guardar actividades planeadas
                    for actividad in pagare_data['planeado']:
                        PagarePlaneado.objects.update_or_create(
                            Pagare=pagare,
                            Actividad_id=actividad['actividad_id'],
                            defaults={'Horas_Planeadas': actividad['horas']}
                        )

                    # Guardar actividades ejecutadas
                    for actividad in pagare_data['ejecutado']:
                        PagareEjecutado.objects.update_or_create(
                            Pagare=pagare,
                            Actividad_id=actividad['actividad_id'],
                            defaults={'Horas_Ejecutadas': actividad['horas']}
                        )

                return JsonResponse({'estado': 'exito', 'mensaje': 'Datos guardados correctamente (JSON)'})

            # Versión para formulario tradicional
            else:
                for key, value in request.POST.items():
                    # Procesar horas planeadas
                    if key.startswith('horas_'):
                        partes = key.split('_')
                        documento = partes[1]
                        actividad_id = partes[2]
                        
                        PagarePlaneado.objects.update_or_create(
                            Pagare_id=documento,
                            Actividad_id=actividad_id,
                            defaults={'Horas_Planeadas': value}
                        )
                    
                    # Procesar horas ejecutadas
                    elif key.startswith('ejecutado_'):
                        partes = key.split('_')
                        documento = partes[1]
                        actividad_id = partes[2]
                        
                        PagareEjecutado.objects.update_or_create(
                            Pagare_id=documento,
                            Actividad_id=actividad_id,
                            defaults={'Horas_Ejecutadas': value}
                        )

                return JsonResponse({'estado': 'exito', 'mensaje': 'Datos guardados correctamente (Formulario)'})
            
        except Exception as e:
            return JsonResponse({'estado': 'error', 'mensaje': str(e)}, status=500)
    
    return JsonResponse({'estado': 'error', 'mensaje': 'Método no permitido'}, status=400)