from openpyxl import Workbook
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from django.db import models
from .models import Certificacion, TiemposConcepto
from .forms import TiemposConceptoForm
from .models import Tiempos_Cliente
from .forms import Tiempos_ClienteForm
from .models import Detalle_Certificacion
from .models import Empleado
from .forms import EmpleadoFilterForm
from .models import TiposContactos
from .forms import TiposContactosForm
from .models import Contactos
from .forms import ContactosForm
from .models import Historial_Cargos
from .forms import HistorialCargosForm
from .models import Moneda
from .forms import MonedaForm
from .models import ClientesContratos
from .forms import ClientesContratosForm
from .models import Referencia
from .forms import ReferenciaForm
from .models import CentrosCostos
from .forms import CentrosCostosForm
from .forms import ActividadPagare
from .forms import PagareFilterForm
from .models import Pagare
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def inicio(request):
    return render(request, 'paginas/Inicio.html')

def nosotros(request):
    return render(request, 'paginas/nosotros.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'Login/login.html', {'form': { 'errors': True }})
    else:
        return render(request, 'Login/login.html', {'form': {}})

def logout_view(request):
    logout(request)
    return redirect('login')

























