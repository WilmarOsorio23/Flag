import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
import Modulo
from Modulo.forms import INDForm
from Modulo.models import IND
from django.views.decorators.csrf import csrf_exempt


def ind_index(request):
    ind_data = IND.objects.all().order_by('-Anio','Mes')
    return render(request, 'ind/ind_index.html', {'ind_data': ind_data})

def ind_crear(request):
    if request.method == 'POST':
        form = INDForm(request.POST)
        if form.is_valid():
            max_id = IND.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_ind = form.save(commit=False)
            nuevo_ind.id = new_id
            nuevo_ind.save()
            return redirect('ind_index')
    else:
        form = INDForm()
    return render(request, 'ind/ind_form.html', {'form': form})

@csrf_exempt
def ind_editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ind = get_object_or_404( IND, pk=id)
            ind.Anio = data.get('Anio', ind.Anio) 
            ind.Mes = data.get('Mes', ind.Mes) 
            ind.Indice = data.get('Indice', ind.Indice)
            ind.save()
            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Modulo.DoesNotExist:
            return JsonResponse({'status': 'error', 'errors': ['Ind no encontrado']})
        except ValueError as ve:
            return JsonResponse({'status': 'error', 'errors': ['Error al procesar los datos: ' + str(ve)]})
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': ['Error desconocido: ' + str(e)]})
    return JsonResponse({'status': 'error', 'error': 'Método no permitido'})
    
def ind_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        IND.objects.filter(id__in=item_ids).delete()
        return redirect('ind_index')
    return redirect('ind_index')

def ind_descargar_excel(request):
    print("inicio descarga")
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        print(item_ids)
        ind_data = IND.objects.filter(id__in=item_ids)

        if not ind_data.exists():
            messages.error(request, "No se encontraron datos para descargar.")
            return redirect('ind_index')
        
        data = []
        for ind in ind_data:    
            data.append([ind.id, ind.Anio, ind.Mes, ind.Indice])

        df = pd.DataFrame(data, columns=['Id', 'Año', 'Mes', 'Incice'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="ind.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('ind_index')