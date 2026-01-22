import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from Modulo.forms import MonedaForm
from Modulo.models import Moneda, Tarifa_Clientes
from Modulo.models import Tarifa_Consultores
from django.contrib import messages
from django.db import models
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_moneda')
def moneda_index(request):
    monedas = Moneda.objects.all()
    return render(request, 'Moneda/MonedaIndex.html', {'monedas': monedas})  

@login_required
@verificar_permiso('can_manage_moneda')
def moneda_crear(request):
  if request.method == 'POST':
        form = MonedaForm(request.POST)
        if form.is_valid():
            max_id = Moneda.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_moneda = form.save(commit=False)
            nuevo_moneda.id = new_id
            nuevo_moneda.save()
        return redirect('moneda_index')
  else:
     form = MonedaForm()
     return render(request, 'Moneda/MonedaForm.html', {'form': form})

@login_required
@verificar_permiso('can_manage_moneda')
def moneda_editar(request, id):
     if request.method == 'POST':
        try:
            data = json.loads(request.body)
            moneda = get_object_or_404( Moneda, pk=id)
            moneda.Nombre= data.get('nombre',moneda.Nombre)
            moneda.descripcion = data.get('descripcion', moneda.descripcion)
            moneda.save()

            print(JsonResponse({'status': 'success'}))
            return JsonResponse({'status': 'success'})
        except Moneda.DoesNotExist:
            return JsonResponse({'error': 'Moneda no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
     else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_moneda')   
def moneda_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Moneda.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'Las monedas seleccionadas se han eliminado correctamente.')
        return redirect('moneda_index')
    return redirect('moneda_index')

@login_required
@verificar_permiso('can_manage_moneda')
def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Tarifa_Consultores.objects.filter(monedaId=id).exists() or
                Tarifa_Clientes.objects.filter(monedaId=id).exists()
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
@verificar_permiso('can_manage_moneda')
def moneda_descargar_excel(request):
    if request.method == 'POST':
        moneda_ids = request.POST.get('items_to_download')
        moneda_ids = list(map(int, moneda_ids.split (',')))
        moneda = Moneda.objects.filter(id__in=moneda_ids)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Moneda.xlsx"'

        data = []
        for monedas in moneda:
            data.append([monedas.id,
                         monedas.Nombre,
                         monedas.descripcion])
        df = pd.DataFrame(data, columns=['Id','Moneda','Descripcion'])
        df.to_excel(response, index=False)
        return response
    return redirect('moneda_index')