# Vista Tipo Documento
import json
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from Modulo import models
from django.db import models
from Modulo.forms import TipoDocumentoForm
from Modulo.models import Clientes, Empleado, TipoDocumento


def tipo_documento_index(request):
    tipo_documentos = TipoDocumento.objects.all()
    return render(request, 'Tipo_Documento/tipo_documento_index.html', {'tipo_documentos': tipo_documentos})

def tipo_documento_crear(request):
    if request.method == 'POST':
        form = TipoDocumentoForm(request.POST)
        if form.is_valid():
            # Obtener el valor máximo actual de TipoDocumentoID
            max_id = TipoDocumento.objects.all().aggregate(max_id=models.Max('TipoDocumentoID'))['max_id']
            new_id = max_id + 1 if max_id is not None else 1
            nuevo_tipo_documento = form.save(commit=False)
            nuevo_tipo_documento.TipoDocumentoID = new_id  # Asignar manualmente el nuevo ID
            nuevo_tipo_documento.save()
            return redirect('tipo_documento_index')
    else:
        form = TipoDocumentoForm()
    return render(request, 'Tipo_Documento/tipo_documento_form.html', {'form': form})

@csrf_exempt
def tipo_documento_editar(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            tipo_documento = TipoDocumento.objects.get(pk=id)
            form = TipoDocumentoForm(data, instance=tipo_documento)

            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except TipoDocumento.DoesNotExist:
            return JsonResponse({'error': 'Módulo no encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error en el formato de los datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def tipo_documento_eliminar(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')
        TipoDocumento.objects.filter(TipoDocumentoId__in=item_ids).delete()
        return redirect('tipo_documento_index')
    return redirect('tipo_documento_index')

def verificar_relaciones(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        ids = data.get('ids', [])

        # Verifica si los módulos están relacionados
        relacionados = []
        for id in ids:
            if (
                Empleado.objects.filter(TipoDocumentoId=id).exists() or
                Clientes.objects.filter(TipoDocumentoId=id).exists()
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

def tipo_documento_descargar_excel(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('items_to_delete')  
        print(item_ids) 

        # Filtra los datos de la tabla TipoDocumento según los IDs seleccionados
        tipo_documento_data = TipoDocumento.objects.filter(TipoDocumentoID__in=item_ids)

        # Verifica si existen datos seleccionados
        if not tipo_documento_data.exists():
            messages.error(request, "No se encontraron datos para descargar.")  # Aquí usas messages
            return redirect('tipo_documento_index')

        # Prepara los datos para exportar
        data = []
        for tipo_documento in tipo_documento_data:
            data.append([tipo_documento.TipoDocumentoID, tipo_documento.Nombre])

        # Crea un DataFrame con los datos obtenidos
        df = pd.DataFrame(data, columns=['TipoDocumentoID', 'Nombre'])

        # Configura la respuesta HTTP para enviar el archivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="tipo_documentos.xlsx"'

        # Escribe el DataFrame al archivo Excel
        df.to_excel(response, index=False)

        # Retorna el archivo al cliente para descargar
        return response

    # Redirige a la página principal si no es un método POST
    return redirect('tipo_documento_index')