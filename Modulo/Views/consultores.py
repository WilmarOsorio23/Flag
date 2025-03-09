# Vista para la tabla Consultores
from datetime import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo.forms import ConsultoresForm
from Modulo.models import Consultores, Empleado, Linea, Modulo, Perfil
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


def consultores_index(request):
    consultores = Consultores.objects.all()
    form = ConsultoresForm()
    return render(request, 'consultores/consultores_index.html', {'consultores': consultores, 'form': form})

def consultores_crear(request):
    if request.method == 'POST':
        form = ConsultoresForm(request.POST)
        if form.is_valid():
            nuevo_consultor = form.save(commit=False)
            nuevo_consultor.save()
            return redirect('consultores_index')
    else:
        form = ConsultoresForm()
    
    return render(request, 'consultores/consultores_form.html', {'form': form})

@csrf_exempt
def consultores_editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            consultor = get_object_or_404(Consultores, Documento=id)

            consultor.Nombre = data.get('Nombre', consultor.Nombre)
            consultor.Empresa = data.get('Empresa', consultor.Empresa)
            consultor.Profesion = data.get('Profesion', consultor.Profesion)

            # Obtener instancias de modelos relacionados
            consultor.LineaId = get_object_or_404(Linea, pk=data.get('LineaId')) if data.get('LineaId') else consultor.LineaId
            consultor.ModuloId = get_object_or_404(Modulo, pk=data.get('ModuloId')) if data.get('ModuloId') else consultor.ModuloId
            consultor.PerfilId = get_object_or_404(Perfil, pk=data.get('PerfilId')) if data.get('PerfilId') else consultor.PerfilId
            

            consultor.Estado = data.get('Estado', consultor.Estado) == 'True'
            consultor.Fecha_Ingreso = data.get('Fecha_Ingreso', consultor.Fecha_Ingreso)
            consultor.Fecha_Retiro = data.get('Fecha_Retiro', consultor.Fecha_Retiro) or None
            consultor.Telefono = data.get('Telefono', consultor.Telefono) or None
            consultor.Direccion = data.get('Direccion', consultor.Direccion) or None
            consultor.Fecha_Operacion = data.get('Fecha_Operacion', consultor.Fecha_Operacion) or None
            consultor.Certificado = data.get('Certificado', consultor.Certificado)
            consultor.Certificaciones = data.get('Certificaciones', consultor.Certificaciones) or None
            consultor.Fecha_Nacimiento = data.get('Fecha_Nacimiento', consultor.Fecha_Nacimiento)
            consultor.Anio_Evaluacion = data.get('Anio_Evaluacion', consultor.Anio_Evaluacion) or None
            consultor.NotaEvaluacion = data.get('NotaEvaluacion', consultor.NotaEvaluacion) or None

            # Validación adicional: Si Estado es False y no hay Fecha_Retiro, no permitir guardar
            if not consultor.Estado and not consultor.Fecha_Retiro:
                return JsonResponse({'error': 'No se puede desactivar un consultor sin una fecha de retiro.'}, status=400)

            consultor.full_clean()
            consultor.save()

            return JsonResponse({'status': 'success'})
        except Consultores.DoesNotExist:
            return JsonResponse({'error': 'Consultor no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
        except Exception as e:
            # Capturar cualquier otra excepción y registrar el error
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    

def consultores_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Consultores.objects.filter(Documento__in=item_ids).delete()
        messages.success(request, 'Los Empleados seleccionados se han eliminado correctamente.')
        return redirect('consultores_index')    
    return redirect('consultores_index')

def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])
        try:
                # Verifica si los módulos están relacionados
                relacionados = []
                for id in ids:
                    if (
                        Empleado.objects.filter(CargoId=id).exists()
                    ): 
                        relacionados.append(id)

                if relacionados:
                    return JsonResponse({
                        'isRelated': True,
                        'ids': relacionados
                    })
                else:
                    return JsonResponse({'isRelated': False})
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    return JsonResponse({'error': 'Cargo no permitido'}, status=405)

def make_timezone_unaware(fecha):
    # Verifica si la fecha es un objeto datetime con zona horaria
    if isinstance(fecha, datetime) and fecha.tzinfo is not None:
        return fecha.replace(tzinfo=None)  # Eliminar zona horaria
    return fecha  # No hacer nada si es un objeto date o ya no tiene zona horaria


def consultores_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete', '').split(',')
        consultores_data = Consultores.objects.filter(Documento__in=item_ids)
        data = []

        if not item_ids or all(id.strip() == '' for id in item_ids):
            return JsonResponse({'error': 'No se seleccionaron elementos para descargar'}, status=400)
        
        else:
            for consultor in consultores_data:
                fecha_ingreso = make_timezone_unaware(consultor.Fecha_Ingreso)
                fecha_retiro = make_timezone_unaware(consultor.Fecha_Retiro)
                fecha_operacion = make_timezone_unaware(consultor.Fecha_Operacion)
                fecha_nacimiento = make_timezone_unaware(consultor.Fecha_Nacimiento)

                data.append([
                    consultor.TipoDocumentoID or '-',
                    consultor.Documento or '-',
                    consultor.Nombre or '-',
                    consultor.Empresa or '-',
                    consultor.Profesion or '-',
                    consultor.LineaId or '-',
                    consultor.ModuloId or '-',
                    consultor.PerfilId or '-',
                    consultor.Estado if consultor.Estado is not None else '-',
                    fecha_ingreso if fecha_ingreso is not None else '-',
                    fecha_retiro if fecha_retiro is not None else '-',
                    consultor.Telefono or '-',
                    consultor.Direccion or '-',
                    fecha_operacion if fecha_operacion is not None else '-',
                    consultor.Certificado if consultor.Certificado is not None else '-',
                    consultor.Certificaciones or '-',
                    fecha_nacimiento if fecha_nacimiento is not None else '-',
                    consultor.Anio_Evaluacion or '-',
                    consultor.NotaEvaluacion or '-',
                ])

            df = pd.DataFrame(data, columns=[
                'Tipo Documento ID',
                'Documento ID',
                'Nombre',
                'Empresa',
                'Profesión',
                'Línea ID',
                'Módulo ID',
                'Perfil ID',
                'Estado',
                'Fecha Ingreso',
                'Fecha Retiro',
                'Teléfono',
                'Dirección',
                'Fecha Operación',
                'Certificado',
                'Certificaciones',
                'Fecha_Nacimiento',
                'Anio_Evaluacion',
                'NotaEvaluacion'
            ])

            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="consultores.xlsx"'

            df.to_excel(response, index=False)

            return response

    return redirect('consultores_index')
