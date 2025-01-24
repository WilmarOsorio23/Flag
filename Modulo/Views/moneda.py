import json
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo.forms import MonedaForm
from Modulo.models import Moneda


def moneda_index(request):
    moneda = Moneda.objects.all()
    return render(request, 'Moneda/Moneda_index.html', {'moneda': moneda})  

def moneda_crear(request):
    if request.method == 'POST':
        form = MonedaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('moneda_index')
    else:
        form = MonedaForm()
    return render(request, 'Moneda/Moneda_form.html', {'form': form})   

def moneda_editar(request, id):
    moneda = get_object_or_404(Moneda, id=id)
    if request.method == 'POST':
        form = MonedaForm(request.POST, instance=moneda)
        if form.is_valid():
            form.save()
            return redirect('moneda_index')
    else:
        form = MonedaForm(instance=moneda)
    return render(request, 'Moneda/Moneda_form.html', {'form': form})   

def verificar_relaciones(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])

def moneda_eliminar(request, id):
    moneda = get_object_or_404(Moneda, id=id)
    moneda.delete()
    return redirect('moneda_index') 


def moneda_descargar_excel(request):
    moneda = Moneda.objects.all()
    data = []
    for moneda in moneda:
        data.append([moneda.id, moneda.descripcion])
    df = pd.DataFrame(data, columns=['Id', 'Descripción'])
    response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') # type: ignore
    response['Content-Disposition'] = 'attachment; filename=moneda.xlsx'
    return response
