# Modulo/Views/Nomina.py
import json
import pandas as pd

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt  # puedes quitarlo si quieres forzar CSRF
from django.contrib.auth.decorators import login_required

from Modulo.forms import NominaForm
from Modulo.models import Clientes, Empleado, Nomina
from Modulo.decorators import verificar_permiso


@login_required
@verificar_permiso('can_manage_nomina')
def nomina_index(request):
    """
    Lista de registros de nómina ordenados por año/mes (descendente)
    y formulario base para selects de cliente en la tabla.
    """
    nomina_data = (
        Nomina.objects
        .select_related('Documento', 'Cliente')
        .all()
        .order_by('-Anio', 'Mes')
    )
    form = NominaForm()
    return render(
        request,
        'nomina/nomina_index.html',
        {
            'nomina_data': nomina_data,
            'form': form,
        },
    )


@login_required
@verificar_permiso('can_manage_nomina')
def nomina_crear(request):
    """
    Crear un nuevo registro de nómina mediante NominaForm.
    """
    if request.method == 'POST':
        form = NominaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('nomina_index')
    else:
        form = NominaForm()

    return render(request, 'Nomina/nomina_form.html', {'form': form})


@login_required
@verificar_permiso('can_manage_nomina')
@csrf_exempt  # si quieres forzar CSRF, quita esto (el JS ya manda X-CSRFToken)
def nomina_editar(request, id):
    """
    Edita un registro puntual de nómina vía fetch (JSON).
    Por ahora solo actualiza Salario y Cliente.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)

    nomina = get_object_or_404(Nomina, pk=id)

    # Salario (se espera un número en formato plano, sin currency_format)
    salario = data.get('Salario')
    if salario is not None:
        try:
            # Limpieza básica por si vienen puntos de miles o comas decimales
            salario_str = str(salario).replace('.', '').replace(',', '.')
            nomina.Salario = salario_str
        except Exception:
            return JsonResponse({'error': 'Formato de salario no válido'}, status=400)

    # Cliente (pk)
    cliente_id = data.get('Cliente')
    if cliente_id:
        cliente = get_object_or_404(Clientes, pk=cliente_id)
        nomina.Cliente = cliente

    nomina.save()
    return JsonResponse({'status': 'success'})


@login_required
@verificar_permiso('can_manage_nomina')
def nomina_eliminar(request):
    """
    Elimina uno o varios registros de nómina seleccionados en la tabla.
    """
    if request.method != 'POST':
        return redirect('nomina_index')

    item_ids = request.POST.getlist('items_to_delete')
    if item_ids:
        Nomina.objects.filter(pk__in=item_ids).delete()

    return redirect('nomina_index')


@login_required
@verificar_permiso('can_manage_nomina')
def verificar_relaciones(request):
    """
    Verifica relaciones antes de eliminar.
    Para Nómina, normalmente NO hay FK que apunten a Nomina,
    así que por defecto permitimos eliminar.
    Dejamos el endpoint implementado y listo para extender si se requieren
    restricciones futuras.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)

    # Si llegáramos a tener relaciones fuertes desde otros modelos a Nomina,
    # aquí sería el lugar para validar. Por ahora, devolvemos que NO hay relaciones.
    relacionados = []

    # Ejemplo futuro:
    # for nomina_id in ids:
    #     if SomeOtherModel.objects.filter(nomina_id=nomina_id).exists():
    #         relacionados.append(nomina_id)

    if relacionados:
        return JsonResponse({'isRelated': True, 'ids': relacionados})
    return JsonResponse({'isRelated': False})


@login_required
@verificar_permiso('can_manage_nomina')
def nomina_descargar_excel(request):
    """
    Descarga en Excel las filas seleccionadas en la tabla.
    Usa pandas para armar el archivo.
    """
    if request.method != 'POST':
        return redirect('nomina_index')

    items_selected = request.POST.get('items_to_download', '')
    if not items_selected:
        return HttpResponse("No se seleccionaron elementos para descargar.", status=400)

    try:
        ids = list(map(int, items_selected.split(',')))
    except ValueError:
        return HttpResponse("IDs de nómina inválidos.", status=400)

    nominas = (
        Nomina.objects
        .select_related('Documento', 'Cliente')
        .filter(NominaId__in=ids)
    )

    if not nominas.exists():
        return HttpResponse("No se encontraron registros de nómina.", status=404)

    data = []
    for nomina in nominas:
        data.append([
            nomina.Anio,
            nomina.Mes,
            nomina.Documento.Documento if nomina.Documento else '',
            nomina.Documento.Nombre if nomina.Documento else '',
            nomina.Salario,
            nomina.Cliente.Nombre_Cliente if nomina.Cliente else '',
        ])

    df = pd.DataFrame(
        data,
        columns=['Año', 'Mes', 'Documento', 'Nombre Empleado', 'Salario', 'Cliente'],
    )

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Nomina.xlsx"'

    df.to_excel(response, index=False)
    return response
