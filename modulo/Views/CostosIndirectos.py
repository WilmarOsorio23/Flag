# Vista Costo Indirecto
import json
from pyexpat.errors import messages
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from modulo import models
from django.db import models
from modulo.forms import CostosIndirectosForm
from modulo.models import Costos_Indirectos, Detalle_Costos_Indirectos
from modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_costos_indirectos')
def costos_indirectos_index(request):
    costos_indirectos = Costos_Indirectos.objects.all()
    return render(request, 'CostosIndirectos/CostosIndirectoIndex.html', {'costos_indirectos': costos_indirectos})

@login_required
@verificar_permiso('can_manage_costos_indirectos')
def costos_indirectos_crear(request):
    if request.method == 'POST':
        form = CostosIndirectosForm(request.POST)
        if form.is_valid():
            max_id = Costos_Indirectos.objects.all().aggregate(max_id=models.Max('CostoId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_costo = form.save(commit=False)
            nuevo_costo.CostoId = new_id
            nuevo_costo.save()
            return redirect('costos_indirectos_index')
    else:
        form = CostosIndirectosForm()
    return render(request, 'CostosIndirectos/CostosIndirectoForms.html', {'form': form})

@login_required
@verificar_permiso('can_manage_costos_indirectos')
@csrf_exempt
def costos_indirectos_editar(request, id):
    if request.method == 'POST':
        try:
            # Cargar los datos enviados como JSON
            data = json.loads(request.body.decode('utf-8'))
            # Obtener el objeto correspondiente
            costo = get_object_or_404(Costos_Indirectos, pk=id)
            # Instanciar el formulario con los datos y el objeto a editar
            form = CostosIndirectosForm(data, instance=costo)

            # Validar y guardar el formulario
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Costos_Indirectos.DoesNotExist:
            return JsonResponse({'error': 'Costo indirecto no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_costos_indirectos')
def costos_indirectos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        Costos_Indirectos.objects.filter(CostoId__in=item_ids).delete()
        messages.success(request, 'Los costos indirectos seleccionados se han eliminado correctamente.')
        return redirect('costos_indirectos_index')
    return redirect('costos_indirectos_index')

@login_required
@verificar_permiso('can_manage_costos_indirectos')
def verificar_relaciones(request):
    print("entro a Verificando relaciones de costos indirectos")
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Detalle_Costos_Indirectos.objects.filter(CostosId=id).exists() 
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
@verificar_permiso('can_manage_costos_indirectos')
def costos_indirectos_descargar_excel(request):
    # Verifica si la solicitud es POST
    if request.method == 'POST':
        # Obtén los IDs enviados desde el formulario
        costos_ids = request.POST.get('items_to_delete')

        # Convierte la cadena de IDs en una lista de enteros
        try:
            costos_ids = list(map(int, costos_ids.split(',')))  # Asegúrate de manejar excepciones aquí
        except (ValueError, AttributeError):
            return HttpResponse("Error al procesar los datos enviados.", status=400)

        # Filtra los objetos correspondientes
        costos = Costos_Indirectos.objects.filter(CostoId__in=costos_ids)

        # Crea una respuesta HTTP con el tipo de contenido de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="CostosIndirectos.xlsx"'

        # Prepara los datos para exportar
        data = []
        for costo in costos:
            data.append([costo.CostoId, costo.Costo])

        # Convierte los datos a un DataFrame de pandas y luego a Excel
        df = pd.DataFrame(data, columns=['ID', 'Costo'])
        df.to_excel(response, index=False)

        return response

    return redirect('costos_indirectos_index')
