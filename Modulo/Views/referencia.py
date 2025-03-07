#Referencia
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
import pandas as pd
from Modulo import models
from Modulo.forms import ReferenciaForm
from Modulo.models import Referencia, Tarifa_Clientes
from django.contrib import messages
from django.db import models

def referencia_index(request):
    Referencias = Referencia.objects.all()
    return render(request, 'referencia/referencia_index.html', {'Referencias': Referencias})

def referencia_crear(request):
    if request.method == 'POST':
        form = ReferenciaForm(request.POST)
        if form.is_valid():
            max_id = Referencia.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nueva_rev = form.save(commit=False)
            nueva_rev .id = new_id
            nueva_rev .save()
        return redirect('referencia_index')
    else:
     form = ReferenciaForm()
     return render(request, 'referencia/referencia_form.html', {'form': form})

def referencia_editar(request, id):
    print("llego a editar d e referencia")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("esta es la data: ",data)
            ref = get_object_or_404( Referencia, pk=id)
            print("este es la variable del registro que encontro por id: ", ref)
            ref.codigoReferencia= data.get('Codigo',ref.codigoReferencia)
            ref.descripcionReferencia = data.get('Descripcion', ref.descripcionReferencia)
            ref.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})  
        except Referencia.DoesNotExist:
            return JsonResponse({'error': 'Moneda no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def referencia_eliminar(request):
   if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Referencia.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'La referencia seleccionada se han eliminado correctamente.')
        return redirect('referencia_index')

def verificar_relaciones(request):
    print("llego a verificar relaciones de referencia")
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Tarifa_Clientes.objects.filter(referenciaId=id).exists()
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


def referencia_descargar_excel(request):
        # Verifica si la solicitud es POST
        if request.method == 'POST':
            referencia_ids = request.POST.get('items_to_download')  
            referencia_ids = list(map(int, referencia_ids.split (','))) 
            referencia = Referencia.objects.filter(id__in=referencia_ids)
    
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="Referencia.xlsx"'

            data = []
            for referencias in referencia:
                data.append([referencias.id,
                             referencias.codigoReferencia,
                             referencias.descripcionReferencia])
            df = pd.DataFrame(data, columns=['Id','Codigo','Descripcion'])
            df.to_excel(response, index=False)
            return response
        return redirect('referencia_index')