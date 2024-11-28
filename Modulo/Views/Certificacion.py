# Vista Certificacion
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import pandas as pd
from Modulo import models
from django.db import models
from Modulo.forms import CertificacionForm
from Modulo.models import Certificacion


def certificacion_index(request):
    certificaciones = Certificacion.objects.all()
    return render(request, 'Certificacion/certificacion_index.html', {'certificaciones': certificaciones})

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


def certificacion_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Certificacion.objects.filter(CertificacionId__in=item_ids).delete()
        return redirect('certificacion_index')
    return redirect('certificacion_index')

def certificacion_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        certificacion_data = Certificacion.objects.filter(CertificacionId__in=item_ids)

        data = []
        for certificacion in certificacion_data:
            data.append([certificacion.CertificacionId, certificacion.Certificacion])

        df = pd.DataFrame(data, columns=['Id Certificación', 'Certificación'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="certificaciones.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('certificacion_index')
