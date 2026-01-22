import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import pandas as pd
from modulo import models
from modulo.forms import IPCForm
from modulo.models import IPC
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.contrib import messages
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_ipc')
def ipc_index(request):
    ipc_data = IPC.objects.all().order_by('-Anio','Mes')
    return render(request, 'IPC/IpcIndex.html', {'ipc_data': ipc_data})

@login_required
@verificar_permiso('can_manage_ipc')
def ipc_crear(request):
    if request.method == 'POST':
        form = IPCForm(request.POST)
        if form.is_valid():
            max_id = IPC.objects.all().aggregate(max_id=models.Max('id'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_ipc = form.save(commit=False)
            nuevo_ipc.id = new_id
            nuevo_ipc.save()
            return redirect('ipc_index')
    else:
        form = IPCForm()
    return render(request, 'IPC/IpcForm.html', {'form': form})

@login_required
@verificar_permiso('can_manage_ipc')
@csrf_exempt 
def ipc_editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            ipc = IPC.objects.get(pk=id)
            form = IPCForm(data, instance=ipc)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except IPC.DoesNotExist:
            return JsonResponse({'error': 'Módulo no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_ipc')
def ipc_eliminar(request):
   if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        IPC.objects.filter(id__in=item_ids).delete()
        messages.success(request, 'El registro se han eliminado correctamente.')
        return redirect('ipc_index')

@login_required
@verificar_permiso('can_manage_ipc')
def ipc_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        print(item_ids)  # Verifica qué valores se están enviando.
        ipc_data = IPC.objects.filter(id__in=item_ids)

        if not ipc_data.exists():
            messages.error(request, "No se encontraron datos para descargar.")
            return redirect('ipc_index')

        data = []
        for ipc in ipc_data:
            data.append([ipc.id, ipc.Anio, ipc.Mes, ipc.Indice])

        df = pd.DataFrame(data, columns=['Id', 'Año', 'Mes', 'Campo Numérico'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="ipc.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('ipc_index')