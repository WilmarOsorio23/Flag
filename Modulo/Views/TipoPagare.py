import json
from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.contrib import messages
import pandas as pd
from django.http import HttpResponseBadRequest
from Modulo.models import TipoPagare
from Modulo.forms import TipoPagareForm
from Modulo.decorators import verificar_permiso
from django.contrib.auth.decorators import login_required

@login_required
@verificar_permiso('can_manage_tipo_pagare')
def tipo_pagare_index(request):
    tipos_pagare = TipoPagare.objects.all()
    return render(request, 'Tipo_Maestro/TipoPagare_index.html', {
        'tipos_pagare': tipos_pagare
    })

@login_required
@verificar_permiso('can_manage_tipo_pagare')
def tipo_pagare_crear(request):
    if request.method == 'POST':
        form = TipoPagareForm(request.POST)
        if form.is_valid():
            try:
                tipo_pagare = form.save()
                print(f"Tipo de Pagaré creado: ID={tipo_pagare.Tipo_PagareId}, Descripción={tipo_pagare.Desc_Tipo_Pagare}")
                messages.success(request, '¡Registro creado con éxito!')
                return redirect('tipo_pagare_index')
            except IntegrityError:
                messages.error(request, '¡El código ya existe!')
                return render(request, 'Tipo_Maestro/TipoPagare_crear.html', {'form': form})
    else:
        form = TipoPagareForm()
    
    return render(request, 'Tipo_Maestro/TipoPagare_crear.html', {'form': form})

@login_required
@verificar_permiso('can_manage_tipo_pagare')
def tipo_pagare_editar(request, id):
    try:
        tipo_pagare = get_object_or_404(TipoPagare, Tipo_PagareId=id)

        if request.method == 'POST':
            # Verifica si la solicitud es JSON (AJAX)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                tipo_pagare.Desc_Tipo_Pagare = data.get('Desc_Tipo_Pagare', tipo_pagare.Desc_Tipo_Pagare)
                tipo_pagare.save()
                return JsonResponse({'status': 'success'})
            else:
                # Manejo de solicitudes POST tradicionales (formulario)
                form = TipoPagareForm(request.POST, instance=tipo_pagare)
                if form.is_valid():
                    try:
                        form.save()
                        messages.success(request, '¡Cambios guardados!')
                        return redirect('tipo_pagare_index')
                    except IntegrityError:
                        messages.error(request, '¡El código ya existe!')
        
        # Si no es una solicitud POST, renderiza el formulario
        form = TipoPagareForm(instance=tipo_pagare)
        return render(request, 'Tipo_Maestro/TipoPagare_editar.html', {
            'form': form,
            'tipo_pagare': tipo_pagare
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@verificar_permiso('can_manage_tipo_pagare')
def tipo_pagare_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete', '').split(',')

        # Filtrar solo IDs válidos (números)
        try:
            item_ids = [int(id.strip()) for id in item_ids if id.strip().isdigit()]
        except ValueError:
            messages.error(request, "Los IDs enviados no son válidos.")
            return redirect('tipo_pagare_index')

        if not item_ids:
            messages.error(request, "No se seleccionaron tipos de pagaré para eliminar.")
            return redirect('tipo_pagare_index')

        # Eliminar los registros seleccionados
        TipoPagare.objects.filter(Tipo_PagareId__in=item_ids).delete()
        messages.success(request, "Tipos de pagaré eliminados correctamente.")
        return redirect('tipo_pagare_index')

    return HttpResponseBadRequest("Método no permitido")

@login_required
@verificar_permiso('can_manage_tipo_pagare')
def tipo_pagare_confirmar_delete(request, id):
    tipo_pagare = get_object_or_404(TipoPagare, Tipo_PagareId=id)
    return render(request, 'Tipo_Maestro/TipoPagare_confirmar_delete.html', {
        'tipo_pagare': tipo_pagare
    })

@login_required
@verificar_permiso('can_manage_tipo_pagare')
def tipo_pagare_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.get('items_to_delete', '').split(',')
        
        item_ids = [int(id) for id in item_ids if id.strip().isdigit()]
        
        if not item_ids:
            messages.error(request, "No se seleccionaron tipos de pagaré válidos para descargar.")
            return redirect('tipo_pagare_index')
        
        tipos_pagare = TipoPagare.objects.filter(Tipo_PagareId__in=item_ids)
        
        data = [[tp.Tipo_PagareId, tp.Desc_Tipo_Pagare] for tp in tipos_pagare]
        df = pd.DataFrame(data, columns=['ID Tipo Pagaré', 'Descripción'])
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="tipos_pagare.xlsx"'
        df.to_excel(response, index=False)
        return response
    
    return redirect('tipo_pagare_index')