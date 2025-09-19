# Conceptos
import json
from pyexpat.errors import messages
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from Modulo import models
from django.db import models
from Modulo.forms import ConceptoForm
from Modulo.models import Concepto, TiemposConcepto
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_conceptos')
def conceptos_index(request):
    concepto = Concepto.objects.all()
    return render(request, 'Conceptos/conceptos_index.html', {'conceptos': concepto})

@login_required
@verificar_permiso('can_manage_conceptos')
def conceptos_crear(request):
    if request.method == 'POST':
        form = ConceptoForm(request.POST)
        if form.is_valid():
            # Obtener el valor máximo actual de ConceptoID
            max_id = Concepto.objects.all().aggregate(max_id=models.Max('ConceptoId'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_concepto = form.save(commit=False)
            nuevo_concepto.ConceptoId = new_id  # Asignar manualmente el nuevo ID
            nuevo_concepto.save()
            return redirect('conceptos_index')
    else:
        form = ConceptoForm()
    return render(request, 'conceptos/conceptos_form.html', {'form': form})

@login_required
@verificar_permiso('can_manage_conceptos')
@csrf_exempt
def conceptos_editar(request, id):
    if request.method == 'POST':
        try:
            # Cargar los datos enviados como JSON
            data = json.loads(request.body.decode('utf-8'))
            # Obtener el objeto correspondiente
            concepto = get_object_or_404(Concepto, pk=id)
            # Instanciar el formulario con los datos y el objeto a editar
            form = ConceptoForm(data, instance=concepto)

            # Validar y guardar el formulario
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Concepto.DoesNotExist:
            return JsonResponse({'error': 'Concepto no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@verificar_permiso('can_manage_conceptos')
def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                TiemposConcepto.objects.filter(CostoId=id).exists() 
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
@verificar_permiso('can_manage_conceptos')
def conceptos_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')  # Obtener los IDs seleccionados
        Concepto.objects.filter(ConceptoId__in=item_ids).delete()  # Filtrar y eliminar los conceptos seleccionados
        messages.success(request, 'Los conceptos seleccionados se han eliminado correctamente.')
        return redirect('conceptos_index')  # Cambia 'conceptos_index' al nombre de tu vista de listado si es diferente
    return redirect('conceptos_index')

@login_required
@verificar_permiso('can_manage_conceptos')
def conceptos_descargar_excel(request):
    # Verifica si la solicitud es POST
    if request.method == 'POST':
        itemIds= request.POST.get('items_to_delete', '').split(',')

        # Convierte la cadena de IDs en una lista de enteros
        conceptos = Concepto.objects.filter(ConceptoId__in=itemIds)

        # Crea una respuesta HTTP con el tipo de contenido de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Conceptos.xlsx"'

        data = []
        for concepto in conceptos:
            data.append([concepto.ConceptoId, concepto.Descripcion])

        df = pd.DataFrame(data, columns=['Id', 'Nombre'])
        df.to_excel(response, index=False)

        return response

    return redirect('Conceptos_index')