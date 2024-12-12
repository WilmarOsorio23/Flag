# Nomina
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from Modulo.forms import NominaForm
from Modulo.models import Nomina
from django.db import models


def nomina_index(request):
    nomina_data = Nomina.objects.all()
    return render(request, 'nomina/nomina_index.html', {'nomina_data': nomina_data})

def nomina_crear(request):
    if request.method == 'POST':
        form = NominaForm(request.POST)
        if form.is_valid():
            max_id = Nomina.objects.all().aggregate(max_id=models.Max('Documento'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nueva_nomina = form.save(commit=False)
            nueva_nomina.Documento = new_id  # Asignar un nuevo Documento
            nueva_nomina.save()
            return redirect('nomina_index')
    else:
        form = NominaForm()
    return render(request, 'Nomina/nomina_form.html', {'form': form})


def nomina_editar(request, anio, mes, documento):
    nomina = get_object_or_404(Nomina, anio=anio, mes=mes, documento=documento)

    if request.method == 'POST':
        form = NominaForm(request.POST, instance=nomina)
        if form.is_valid():
            form.save()
            return redirect('nomina_index')
    else:
        form = NominaForm(instance=nomina)

    return render(request, 'nomina/nomina_form.html', {'form': form})

def nomina_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        for item_id in item_ids:
            anio, mes, documento = item_id.split('|')
            Nomina.objects.filter(anio=anio, mes=mes, documento=documento).delete()
        return redirect('nomina_index')
    return redirect('nomina_index')

def nomina_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        nomina_data = []
        for item_id in item_ids:
            anio, mes, documento = item_id.split('|')
            nomina = Nomina.objects.filter(anio=anio, mes=mes, documento=documento).first()
            if nomina:
                nomina_data.append([nomina.anio, nomina.mes, nomina.documento, nomina.salario, nomina.cliente])

        df = pd.DataFrame(nomina_data, columns=['Año', 'Mes', 'Documento', 'Salario', 'Cliente'])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="nomina.xlsx"'

        df.to_excel(response, index=False)

        return response

    return redirect('nomina_index')
