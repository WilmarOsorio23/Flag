# Nomina
import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from Modulo import models
from Modulo.forms import NominaForm
from Modulo.models import Clientes, Empleado, Nomina
from django.db import models
from django.views.decorators.csrf import csrf_exempt

def nomina_index(request):
    nomina_data = Nomina.objects.all().order_by('-Anio','Mes')
    
    return render(request, 'nomina/nomina_index.html', {'nomina_data': nomina_data})

def nomina_crear(request):
    if request.method == 'POST':
        form = NominaForm(request.POST)
        if form.is_valid():
            nueva_nomina = form.save(commit=False)
            nueva_nomina.save()  # Guardar directamente el registro con el Documento proporcionado
            return redirect('nomina_index')
    else:
        form = NominaForm()
    return render(request, 'Nomina/nomina_form.html', {'form': form})
    
@csrf_exempt 
def nomina_editar(request, id):
   print("llego hasta views")
   if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            nomina = Nomina.objects.get(pk=id)
            form = NominaForm(data, instance=nomina)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except Nomina.DoesNotExist:
            return JsonResponse({'error': 'Módulo no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
   else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
   
def nomina_eliminar(request):
    print("llego hasta nomina eliminar")
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        print(item_ids)
    for item_id in item_ids:
            Nomina.objects.filter(pk=item_id).delete()
    return redirect('nomina_index')
  
def verificar_relaciones(request):
   if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Empleado.objects.filter(NominaId=id.Documento).exists() or
                Clientes.objects.filter(NominaId=id.ClienteId).exists()
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
    
def nomina_descargar_excel(request):
    if request.method == 'POST':
        items_selected = request.POST.get('items_to_download')
        items_selected = list(map(int, items_selected.split (','))) 

        nominas = Nomina.objects.filter(NominaId__in=items_selected)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Nomina.xlsx"'

        data = []
        for nomina in nominas:
            data.append([
                nomina.Anio,
                nomina.Mes,
                nomina.Documento.Documento,
                nomina.Documento.Nombre,
                nomina.Salario,
                nomina.Cliente.Nombre_Cliente,
            ])
        df = pd.DataFrame(data, columns=['Año','Mes','Documento','Nombre Empleado','Salario','Cliente'])
        df.to_excel(response, index=False)
        return response
    return redirect('nomina_index')


'''def nomina_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        
        # Verificar si se recibieron IDs
        if not item_ids:
            return HttpResponse("No se seleccionaron elementos para descargar.", status=400)
        
        # Consultar las nóminas usando las IDs
        nomina_data = []
        for item_id in item_ids:
            try:
                nomina = Nomina.objects.get(pk=item_id)
                nomina_data.append([
                    nomina.Anio, 
                    nomina.Mes, 
                    nomina.Documento.Documento, 
                    nomina.Documento.Nombre,
                    nomina.Salario, 
                    nomina.Cliente.Nombre_Cliente
                ])
            except Nomina.DoesNotExist:
                print(f"Nómina con ID {item_id} no encontrada.")
        
        # Si no hay datos para exportar
        if not nomina_data:
            return HttpResponse("No se encontraron registros de nómina.", status=404)

        # Crear DataFrame de pandas
        df = pd.DataFrame(nomina_data, columns=['Año', 'Mes', 'Documento','Nombre Empleado', 'Salario', 'Cliente'])
        
        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="nomina.xlsx"'
        
        # Escribir el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response

    return redirect('nomina_index')'''
    
