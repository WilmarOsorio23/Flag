# Detalle certificacion
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from Modulo.forms import Detalle_CertificacionForm
from Modulo.models import Detalle_Certificacion
from django.db import models
from django.contrib import messages
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_detalle_certificacion')
def detalle_certificacion_index(request):
    detalles_certificacion = Detalle_Certificacion.objects.all()
    #print(detalles_certificacion) 
    return render(request, 'Detalle_Certificacion/detalle_certificacion_index.html', {'detalles_certificacion': detalles_certificacion})

@login_required
@verificar_permiso('can_manage_detalle_certificacion')
def detalle_certificacion_crear(request):
 print("entro a la funcion")
 if request.method == 'POST':
    form = Detalle_CertificacionForm(request.POST)
    if form.is_valid():
        max_id = Detalle_Certificacion.objects.all().aggregate(max_id=models.Max('Id'))['max_id']
        new_id = max_id + 1 if max_id is not None else 1
        nuevo_DC = form.save(commit=False)
        nuevo_DC.Id = new_id
        nuevo_DC.save()
        return redirect('detalle_certificacion_index')
    else:
        form = Detalle_CertificacionForm()
        return redirect('detalle_certificacion_index')
 else:
    form = Detalle_CertificacionForm()
    return render(request, 'Detalle_Certificacion/detalle_certificacion_form.html', {'form': form})

@login_required
@verificar_permiso('can_manage_detalle_certificacion')
def detalle_certificacion_editar(request,Id):
    print("llego hasta editar")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalle = get_object_or_404( Detalle_Certificacion, pk=Id)
            detalle.Fecha_Certificacion = data.get('FechaCertificacion', detalle.Fecha_Certificacion)
            detalle.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Detalle_Certificacion.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_detalle_certificacion')
def detalle_certificacion_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Detalle_Certificacion.objects.filter(Id__in=item_ids).delete()
        messages.success(request, 'Los detalles seleccionados se han eliminado correctamente.')
        return redirect('detalle_certificacion_index')
    return redirect('detalle_certificacion_index')

@login_required
@verificar_permiso('can_manage_detalle_certificacion')
def detalle_certificacion_descargar_excel(request):
    if request.method == 'POST':
        items_selected = request.POST.get('items_to_download')
        items_selected = list(map(int, items_selected.split (','))) 

        detalleCertificacion = Detalle_Certificacion.objects.filter(Id__in=items_selected)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="DetallesCertificacion.xlsx"'

        data = []
        for detalle in detalleCertificacion:
            data.append([
                detalle.Id,
                detalle.Documento.Nombre,
                detalle.Fecha_Certificacion,
                detalle.CertificacionId,
            ])
        df = pd.DataFrame(data, columns=['Id','Nombre Empleado','Fecha','certificacion'])
        df.to_excel(response, index=False)
        return response
    return redirect('detalle_certificacion_index')