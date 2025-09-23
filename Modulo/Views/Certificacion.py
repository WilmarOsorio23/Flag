# Vista Certificacion
import json
from pyexpat.errors import messages
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from Modulo import models
from django.db import models
from Modulo.forms import CertificacionForm
from Modulo.models import Certificacion, Detalle_Certificacion
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_certificacion')
def certificacion_index(request):
    certificaciones = Certificacion.objects.all()
    return render(request, 'Certificacion/certificacion_index.html', {'certificaciones': certificaciones})

@login_required
@verificar_permiso('can_manage_certificacion')
def certificacion_crear(request):
    if request.method == 'POST':
        form = CertificacionForm(request.POST)
        if form.is_valid():
            max_id = Certificacion.objects.all().aggregate(max_id=models.Max('CertificacionId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nueva_certificacion = form.save(commit=False)
            nueva_certificacion.CertificacionId = new_id
            nueva_certificacion.save()
            return redirect('certificacion_index')
    else:
        form = CertificacionForm()
    return render(request, 'Certificacion/certificacion_form.html', {'form': form})

@login_required
@verificar_permiso('can_manage_certificacion')
@csrf_exempt
def certificacion_editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            certificacion = Certificacion.objects.get(pk=id)
            form = CertificacionForm(data, instance=certificacion)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Certificacion.DoesNotExist:
            return JsonResponse({'error': 'Certificación no encontrada'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_certificacion')
def certificacion_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Certificacion.objects.filter(CertificacionId__in=item_ids).delete()
        messages.success(request, 'Las certificaciones seleccionadas se han eliminado correctamente.')
        return redirect('certificacion_index')
    return redirect('certificacion_index')

@login_required
@verificar_permiso('can_manage_certificacion')
def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Detalle_Certificacion.objects.filter(CertificacionId=id).exists() 
            ): 
                relacionados.append(id)

        if relacionados:
            return JsonResponse({
                'isRelated': True,
                'ids': relacionados
            })
        else:
            return JsonResponse({'isRelated': False})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_certificacion')
def certificacion_descargar_excel(request):
    # Verifica si la solicitud es POST
    if request.method == 'POST':
        certificacion_ids = request.POST.get('items_to_delete')  
        
        # Convierte la cadena de IDs en una lista de enteros
        certificacion_ids = list(map(int, certificacion_ids.split (',')))  # Cambiado aquí
        certificacion = Certificacion.objects.filter(CertificacionId__in=certificacion_ids)

        # Crea una respuesta HTTP con el tipo de contenido de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Certificaciones.xlsx"'

        data = []
        for certificaciones in certificacion:
            data.append([certificaciones.CertificacionId, certificaciones.Certificacion])

        df = pd.DataFrame(data, columns=['Id', 'Nombre'])
        df.to_excel(response, index=False)

        return response

    return redirect('Certificacion')
       

