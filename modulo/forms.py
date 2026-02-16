from django import forms
from .models import CustomUser, Facturacion_Consultores, FacturacionClientes, Horas_Habiles, Modulo, IPC, IND, Linea, Pagare, Perfil, TipoDocumento, Clientes, Consultores, Certificacion, Costos_Indirectos, TipoPagare, UserRole
from .models import Concepto, Gastos, Detalle_Gastos, Total_Gastos, Total_Costos_Indirectos
from .models import Detalle_Costos_Indirectos, TiemposConcepto, Tiempos_Cliente, Nomina, Detalle_Certificacion, Empleado
from .models import Cargos
from django import forms
from .models import Modulo
from .models import TiposContactos
from .models import Contactos
from .models import Historial_Cargos
from .models import Empleados_Estudios
from .models import Tarifa_Consultores
from django.core.exceptions import ValidationError
from .models import Moneda
from .models import ClientesContratos
from .models import ContratosOtrosSi
from .models import Tarifa_Clientes
from .models import Referencia
from .models import CentrosCostos
from .models import LineaClienteCentroCostos
from datetime import date, datetime
from .models import ActividadPagare
from datetime import date
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = '__all__'
        widgets = {
            'Modulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la descripción del módulo'
            }),
        }   

class IPCForm(forms.ModelForm):
    class Meta:
        model = IPC
        fields = '__all__'
        widgets = {
            'Anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'Mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
            'Indice': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el Indice'
            }),
        }
        labels = {
            'Anio':'Año',
            'Mes': 'Mes',
            'Indice': 'Índice',
        }

class CargosForm(forms.ModelForm):
    class Meta:
        model = Cargos
        fields = '__all__'
        widgets = {
            'Cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el Cargo'
            }),
        }
        labels = {
            'Cargo': 'Cargo',
        } 

class ClientesForm(forms.ModelForm):
    """
    Formulario para gestionar los datos de los clientes.

    Campos:
        - TipoDocumentoID: Selección del tipo de documento.
        - DocumentoId: Identificación del documento.
        - Nombre_Cliente: Nombre del cliente.
        - Activo: Estado activo del cliente.
        - Fecha_Inicio: Fecha de inicio del cliente.
        - Fecha_Retiro: Fecha de retiro del cliente.
        - Direccion: Dirección del cliente.
        - Telefono: Teléfono del cliente.
        - CorreoElectronico: Correo electrónico del cliente.
        - BuzonFacturacion: Buzón de facturación del cliente.
        - TipoCliente: Tipo de cliente.
        - Ciudad: Ciudad del cliente.
        - Departamento: Departamento del cliente.
        - Pais: País del cliente.
        - Nacional
    """
    class Meta:
        model = Clientes
        fields = [
            'TipoDocumentoID', 'DocumentoId', 'Nombre_Cliente', 'Activo', 
            'Fecha_Inicio', 'Fecha_Retiro', 'Direccion', 'Telefono', 
            'CorreoElectronico', 'BuzonFacturacion', 'TipoCliente', 
            'Ciudad', 'Departamento', 'Pais', 'Nacional', 'ContactoID'
        ]
        widgets = {
            'TipoDocumentoID': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de Documento'
            }),
            'DocumentoId': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Documento ID'
            }),
            'Nombre_Cliente': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre del Cliente'
                }),
            'Activo': forms.Select(choices=[
                (True, 'SI'),
                (False, 'NO')
            ], attrs={
                'class': 'form-control'
                }),
            'Fecha_Inicio': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'Fecha_Retiro': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
                }),
            'Direccion' : forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Direccion',
                
                }),
            'Telefono' : forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Telefono',
                }),
            'CorreoElectronico': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Correo Electrónico',
                }),
            'ContactoID': forms.Select(attrs={
                'class': 'form-control',
                'required': False}),
            'BuzonFacturacion': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Buzón Facturación',
                }),
            'TipoCliente': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Tipo Cliente',
                }),
            'Ciudad': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ciudad',
                }),
            'Departamento': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Departamento',
                }),
            'Pais': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Pais',
                }),
            'Nacional': forms.Select(choices=[
                (True, 'SI'),
                (False, 'NO')
            ], attrs={
                'class': 'form-control'
                })
        } 
    def __init__(self, *args, **kwargs):
        super(ClientesForm, self).__init__(*args, **kwargs)
        self.fields['Direccion'].required = False
        self.fields['Telefono'].required = False
        self.fields['CorreoElectronico'].required = False
        self.fields['BuzonFacturacion'].required = False
        self.fields['TipoCliente'].required = False
        self.fields['Ciudad'].required = False
        self.fields['Departamento'].required = False
        self.fields['Pais'].required = False
        self.fields['ContactoID'].queryset = Contactos.objects.none() 
    
    def clean(self):
        cleaned_data = super().clean()
        activo = cleaned_data.get('Activo')
        fecha_retiro = cleaned_data.get('Fecha_Retiro')

        if not activo and not fecha_retiro:
            raise forms.ValidationError('No se puede desactivar un cliente sin una fecha de retiro.')

        return cleaned_data
        
class INDForm(forms.ModelForm):
    class Meta:
        model = IND
        fields = '__all__'
        widgets = {
            'Anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'Mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
            'Indice': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el Indice'
            }),
        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
            'Indice': 'Índice',
        }
        
class TiposContactosForm(forms.ModelForm):
    class Meta:
        model = TiposContactos
        fields = '__all__'
        widgets = {
            'Descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción'}),
        }
        labels = {
            'Descripcion': 'Descripción',
        }

class ContactosForm(forms.ModelForm):
    contactoId = forms.ModelChoiceField(
        queryset=TiposContactos.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Contacto'
    )
    clienteId = forms.ModelChoiceField( 
        queryset=Clientes.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Cliente'
    )

    class Meta:
        model = Contactos
        fields = '__all__'
        widgets = {
            'Nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre'}),
            'Telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el teléfono'}),
            'telefono_fijo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el teléfono fijo'}),  # Nuevo campo
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el correo electrónico'}),  # Nuevo campo
            'Direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la dirección'}),
            'Cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el cargo'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'Nombre': 'Nombre',
            'Telefono': 'Teléfono',
            'telefono_fijo': 'Teléfono Fijo',  # Nuevo campo
            'correo': 'Correo Electrónico',  # Nuevo campo
            'Direccion': 'Dirección',
            'Cargo': 'Cargo',
            'activo': 'Activo',
        }

class ConsultoresForm(forms.ModelForm):
    """
    Formulario para gestionar los datos de los consultores.

    Campos:
        - TipoDocumentoID: Selección del tipo de documento.
        - Documento: Identificación del documento.
        - Nombre: Nombre del consultor.
        - Empresa: Empresa del consultor.
        - Profesion: Profesión del consultor.
        - LineaId: Selección de la línea.
        - ModuloId: Selección del módulo.
        - PerfilId: Selección del perfil.
        - Estado: Estado del consultor (Activo/Inactivo).
        - Fecha_Ingreso: Fecha de ingreso del consultor.
        - Fecha_Retiro: Fecha de retiro del consultor (opcional).
        - Direccion: Dirección del consultor (opcional).
        - Telefono: Teléfono del consultor (opcional).
        - Fecha_Operacion: Fecha de operación.
        - Certificado: Certificado del consultor (SI/NO).
        - Certificaciones: Certificaciones del consultor.
        - Fecha_Nacimiento: Fecha de nacimiento del consultor.
        - Anio_Evaluacion: Año de evaluación (opcional).
        - NotaEvaluacion: Nota de evaluación (opcional).
    """
    class Meta:
        model = Consultores
        fields = '__all__'
        widgets = {
            'TipoDocumentoID': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de Documento'
            }),
            'Documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Documento'
            }),
            'Nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Consultor'
            }),
            'Empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Empresa'
            }),
            'Profesion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Profesión'
            }),
            'LineaId': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Selecciona Línea'
            }),
            'ModuloId': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Selecciona Módulo'
            }),
            'PerfilId': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Selecciona Perfil'
            }),
            'Estado': forms.Select(
                choices=[
                    (True, 'Activo'),
                    (False, 'Inactivo'),
                ],
                attrs={ 
                    'class': 'form-control'
                }
            ),
            'Fecha_Ingreso': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'Fecha_Retiro': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Fecha de Retiro (opcional)',
            }),
            'Direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección (opcional)'
            }),
            'Telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono (opcional)',
                'type': 'number'
            }),
            'Fecha_Operacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Fecha de Operación'
            }),
            'Certificado': forms.Select(
                choices=[
                    (True, 'SI'),
                    (False, 'NO'),
                ],
                attrs={ 
                    'class': 'form-control'
                }
            ),
            'Certificaciones': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Certificados'
            }),
            'Fecha_Nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'Anio_Evaluacion': forms.TextInput(attrs={
                            'type': 'number',
                            'class': 'form-control',
                            'placeholder': 'Ingrese el año'
            }),
            'NotaEvaluacion': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese la Nota'
            })
            
        }
    def __init__(self, *args, **kwargs):
            """
            Validación personalizada para el modelo Clientes.

            Reglas de validación:
            - CorreoElectronico: Validar que sea un correo electrónico válido.
            - Telefono: Validar que contenga solo números y opcionalmente algunos caracteres especiales como +, -, (), y espacios.
            - BuzonFacturacion: Validar que sea un correo electrónico válido.
            - Ciudad, Departamento y Pais: Validar que no contengan caracteres especiales no permitidos.

            Lanza:
                ValidationError: Si alguna validación falla.
            """
            super().__init__(*args, **kwargs)
            self.fields['Fecha_Retiro'].required = False  # Campo no obligatorio
            self.fields['Fecha_Retiro'].label = "Fecha de Retiro (opcional)"    
            self.fields['LineaId'].empty_label = "Selecciona una Línea"
            self.fields['ModuloId'].empty_label = "Selecciona un Módulo"
            self.fields['PerfilId'].empty_label = "Selecciona un Perfil"
            self.fields['Telefono'].required = False  # Permitir campo vacío
            self.fields['Direccion'].required = False  # Permitir campo vacío
            self.fields['Fecha_Retiro'].required = False  # Permitir campo vacío
            self.fields['Certificado'].required = False  # Permitir campo vacío
            self.fields['Certificaciones'].required = False  # Permitir campo vacío
            self.fields['Anio_Evaluacion'].required = False # Permitir campo vacío
            self.fields['NotaEvaluacion'].required = False # Permitir campo vacío
            
    def clean(self):
        """
        Validación personalizada para el formulario ConsultoresForm.

        Reglas de validación:
        - Si la Fecha de Retiro está presente, el Estado debe ser Inactivo.

        Lanza:
            ValidationError: Si alguna validación falla.
        """
        cleaned_data = super().clean()
        fecha_retiro = cleaned_data.get('Fecha_Retiro')
        estado = cleaned_data.get('Estado')

        if fecha_retiro and estado:
            raise ValidationError('Si la Fecha de Retiro está presente, el Estado debe ser Inactivo.')
        
        return cleaned_data

class ColaboradorFilterForm(forms.Form):

    Empleado = forms.ChoiceField(
        choices=[],  
        required=False, 
        label='Empleado',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Consultor = forms.ChoiceField(
        choices=[],  
        required=False, 
        label='Consultor',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    LineaId = forms.ModelChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    ModuloId = forms.ChoiceField(
        choices=[],
        required=False, 
        label='Módulo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Anio = forms.ChoiceField(
        choices=[],
        required=True,
        label='Año *Obligatorio*',  # Modificado aquí
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Mes = forms.ChoiceField(
        choices=[],
        required=True,
        label='Mes *Obligatorio*',  # Modificado aquí
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    ClienteId = forms.ModelChoiceField(
        queryset=Clientes.objects.all(), 
        required=False, 
        label='Cliente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_empleado()
        self.populate_consultor()
        self.populate_cliente()
        self.populate_anio()
        self.populate_mes()
        self.populate_linea()

    def populate_empleado(self):
        empleados = Empleado.objects.values_list('Documento', 'Nombre').distinct()
        self.fields['Empleado'].choices = [('', 'Seleccione el Empleado')] + list(empleados)

    def populate_consultor(self):
        consultores = Consultores.objects.values_list('Documento', 'Nombre').distinct()
        self.fields['Consultor'].choices = [('', 'Seleccione el Consultor')] + list(consultores)

    def populate_cliente(self):
        clientes = Clientes.objects.values_list('ClienteId', 'Nombre_Cliente').distinct()
        self.fields['ClienteId'].choices = [('', 'Seleccione el cliente')] + list(clientes)

    def populate_anio(self):
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in range(2022, 2026)]

    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = [('', 'Seleccione el mes')] + meses

    def populate_linea(self):
        # Si ModuloId necesita opciones dinámicas, añade lógica aquí.
        linea = Linea.objects.values_list('LineaId', 'Linea').distinct()  # Ajusta según tus modelos
        self.fields['LineaId'].choices = [('', 'Seleccione la linea')] + list(linea)

class LineaForm(forms.ModelForm):
    class Meta:
        model = Linea
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la línea'
            }),
        }
        labels = {
            'nombre': 'Nombre',
        }

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
        }
        labels = {
            'nombre': 'Nombre',
        }

class TipoDocumentoForm(forms.ModelForm):    
    class Meta:
        model = TipoDocumento
        fields = '__all__'
        widgets = {
            'Nombre': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
            'descripcion': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese la descripción'
            }),
        }
        labels = {
            'Nombre': 'Nombre',
            'descripcion': 'Descripción',
        }

class CertificacionForm(forms.ModelForm):
    class Meta:
        model = Certificacion
        fields = '__all__'
        widgets = {
            'Certificacion': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese la certificación'
            }),
        }
        labels = {
            'Certificacion': 'Certificación',
        }

class CostosIndirectosForm(forms.ModelForm):
    class Meta:
        model = Costos_Indirectos
        fields = '__all__'
        widgets = {
            'Costo': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el costo'
            }),
        }
        labels = {
            'Costo': 'Costo',
        }

class ConceptoForm(forms.ModelForm):
    class Meta:
        model = Concepto
        fields = '__all__'
        widgets = {
            'Descripcion': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese la descripción'
            }),
        }
        labels = {
            'Descripcion': 'Descripción',
        }

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gastos
        fields = '__all__'
        widgets = {
            'Gasto': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el gasto'
            }),
        }
        labels = {
            'Gasto': 'Gasto',
        }

class DetalleGastosFormOpcion2(forms.ModelForm):

    GastosId=forms.ModelChoiceField(
        queryset=Gastos.objects.all(),
        widget=forms.Select(attrs={'class':'form-control'}),
        label='Gastos'
    )
    Valor = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese el Valor'}),
        label='Valor'
    )

    class Meta:
        model = Detalle_Gastos
        exclude = ['Anio', 'Mes', 'TotalGastos']

class DetalleGastosForm(forms.ModelForm):

    GastosId=forms.ModelChoiceField(
        queryset=Gastos.objects.all(),
        widget=forms.Select(attrs={
            'class':'form-control'
        }),
        label='Gastos'
    )   

    class Meta:
        model = Detalle_Gastos
        fields = '__all__'
        widgets = {
            'Anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'Mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
            'Valor': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el valor'
            }),
        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
            'Valor': 'Valor',
        }

    def clean(self):
        cleaned_data = super().clean()
        Anio = cleaned_data.get('Anio')
        Mes = cleaned_data.get('Mes')
        GastosId = cleaned_data.get('GastosId')

        if Detalle_Gastos.objects.filter(
            Anio=Anio,
            Mes=Mes,
            GastosId=GastosId
        ).exists():
            raise ValidationError(
                "Ya existe este gasto dentro de este mes y año."
            )  
        return cleaned_data

class TotalGastosForm(forms.ModelForm):
    class Meta:
        model = Total_Gastos
        fields = ['Anio', 'Mes']  
        widgets = {
            'Anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'Mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),

        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
        }

class Total_Costos_IndirectosForm(forms.ModelForm):
    class Meta:
        model = Total_Costos_Indirectos
        fields = ['Anio', 'Mes']  
        widgets = {
            'Anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'Mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.Total = 0  # Se asegura de que siempre empiece en 0
        if commit:
            instance.save()
        return instance

class DetalleCostosIndirectosFormOpcion2(forms.ModelForm):
    CostosId = forms.ModelChoiceField(
        queryset=Costos_Indirectos.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Costos Indirectos'
    )
    Valor = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese el Valor'}),
        label='Valor'
    )

    class Meta:
        model = Detalle_Costos_Indirectos
        exclude = ['Anio', 'Mes', 'TotalCostosIndirectos']


class DetalleCostosIndirectosForm(forms.ModelForm):

    CostosId = forms.ModelChoiceField(
        queryset=Costos_Indirectos.objects.all(),  
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='CostosId'
    )

    class Meta:
        model = Detalle_Costos_Indirectos
        fields = ['CostosId', 'Valor']

    class Meta:
        model = Detalle_Costos_Indirectos
        fields = '__all__'
        widgets = {
            'Anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'Mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
            'Valor': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el Valor'
            }),
        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
            'Valor': 'Valor',
        }
        
        
    def clean(self):
            cleaned_data = super().clean()
            Anio = cleaned_data.get('Anio')
            Mes = cleaned_data.get('Mes')
            CostosId = cleaned_data.get('CostosId')
    
            if Detalle_Costos_Indirectos.objects.filter(
                Anio=Anio,
                Mes=Mes,
                CostosId=CostosId
            ).exists():
                raise ValidationError(
                    "Ya existe este costo dentro de este año y mes."
                )  
            return cleaned_data
        
class TiemposConceptoForm(forms.ModelForm):
    class Meta:
        model = TiemposConcepto
        fields = '__all__'
        widgets = {
            'anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
            'colaborador': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el colaborador'
            }),
            'concepto_id': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el concepto'
            }),
            'horas': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese las horas'
            }),
        }
        labels = {
            'anio': 'Año',
            'mes': 'Mes',
            'colaborador': 'Colaborador',
            'concepto_id': 'Concepto',
            'horas': 'Horas',
        }

class Tiempos_ClienteForm(forms.ModelForm):
    class Meta:
        model = Tiempos_Cliente
        fields = '__all__'
        widgets = {
            'anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
            'colaborador': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del colaborador'
            }),
            'cliente_id': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el ID del cliente'
            }),
            'horas': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese las horas trabajadas'
            }),
        }
        labels = {
            'anio': 'Año',
            'mes': 'Mes',
            'colaborador': 'Colaborador',
            'cliente_id': 'Cliente ID',
            'horas': 'Horas',
        }

class NominaForm(forms.ModelForm):
    Documento=forms.ModelChoiceField(
        queryset=Empleado.objects.all(),
        widget= forms.Select(attrs={
            'class':'form-control'
        }),
        label='Documento'
    )
    Cliente=forms.ModelChoiceField(
        queryset=Clientes.objects.all(),
        widget=forms.Select(attrs={
            'class':'form-control'
        }),
        label='Cliente'
    )
    class Meta:
        model = Nomina
        fields = '__all__'
        widgets = {
            'Anio': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'Mes': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
            'Salario': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el salario'
            })
        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
            'Salario': 'Salario'
        }

    def clean(self):
        cleaned_data = super().clean()
        Anio = cleaned_data.get('Anio')
        Mes = cleaned_data.get('Mes')
        Documento = cleaned_data.get('Documento')

        if Nomina.objects.filter(
            Anio=Anio,
            Mes=Mes,
            Documento=Documento
        ).exists():
            raise ValidationError(
                "Ya existe un registro con el mismo Anio, Mes y Documento."
            )  
        return cleaned_data

class Detalle_CertificacionForm(forms.ModelForm):

    CertificacionId = forms.ModelChoiceField(
        queryset=Certificacion.objects.all(),  
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Certificacion id'
    )

    Documento = forms.ModelChoiceField(
        queryset=Empleado.objects.all(),  
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Documento'
    )

    class Meta:
        model = Detalle_Certificacion
        fields = '__all__'
        widgets = {  
            'Fecha_Certificacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Seleccione la fecha de nacimiento'
            }),
        }
        labels = {
            'Fecha_Certificacion': 'Fecha de Certificación'
        }

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__'
        widgets = {
            'TipoDocumento': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione el tipo de documento'}),
            'Documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el número de documento'}),
            'Nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del empleado'}),
            'FechaNacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Seleccione la fecha de nacimiento'}),
            'FechaIngreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Seleccione la fecha de ingreso'}),
            'FechaOperacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Seleccione la fecha de operación'}),
            'ModuloId': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione el módulo'}),
            'PerfilId': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione el perfil'}),
            'LineaId': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione la línea'}),
            'CargoId': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Ingrese el cargo'}),
            'TituloProfesional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el título profesional'}),
            'FechaGrado': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Seleccione la fecha de grado'}),
            'Universidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la universidad'}),
            'ProfesionRealizada': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la profesión realizada'}),
            'TituloProfesionalActual': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el título profesional actual'}),
            'UniversidadActual': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la universidad actual'}),
            'AcademiaSAP': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Seleccione una opción'), ('1', 'Sí'), ('0', 'No')]),
            'CertificadoSAP': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Seleccione una opción'), ('1', 'Sí'), ('0', 'No')]),
            'OtrasCertificaciones': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Seleccione una opción'), ('1', 'Sí'), ('0', 'No')]),
            'Postgrados': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Seleccione una opción'), ('1', 'Sí'), ('0', 'No')]),
            'Activo': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Seleccione el estado'), ('1', 'Sí'), ('0', 'No')]),
            'FechaRetiro': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Seleccione la fecha de retiro'}),
            'Direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la dirección'}),
            'Ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la ciudad'}),
            'Departamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el departamento'}),
            'DireccionAlterna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la dirección alterna'}),
            'Telefono1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el teléfono 1'}),
            'Telefono2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el teléfono 2'}),
            'Genero': forms.Select(attrs={'class': 'form-control'}, choices=[('', '—'), ('Masculino', 'Masculino'), ('Femenino', 'Femenino')]),
            'EstadoCivil': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Soltero, Casado'}),
            'NumeroHijos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'TarjetaProfesional': forms.Select(attrs={'class': 'form-control'}, choices=[('', '—'), ('1', 'Sí'), ('0', 'No')]),
            'RH': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. O+, A+'}),
            'TipoContrato': forms.Select(attrs={'class': 'form-control'}, choices=[('', '—'), ('Indefinido', 'Indefinido'), ('Fijo', 'Fijo')]),
            'FondoPension': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fondo de pensión'}),
            'EPS': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'EPS'}),
            'FondoCesantias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fondo de cesantías'}),
            'CajaCompensacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Caja de compensación'}),
        }
        labels = {
            'TipoDocumento': 'Tipo de Documento',
            'Documento': 'Documento',
            'Nombre': 'Nombre Completo',
            'FechaNacimiento': 'Fecha de Nacimiento',
            'FechaIngreso': 'Fecha de Ingreso',
            'FechaOperacion': 'Fecha de Operación',
            'ModuloId': 'Módulo',
            'PerfilId': 'Perfil (N/A si aplica)',
            'LineaId': 'Línea',
            'CargoId': 'Cargo',
            'TituloProfesional': 'Título Profesional',
            'FechaGrado': 'Fecha de Grado',
            'Universidad': 'Universidad',
            'ProfesionRealizada': 'Profesión Realizada',
            'TituloProfesionalActual': 'Título Profesional Actual',
            'UniversidadActual': 'Universidad Actual',
            'AcademiaSAP': 'Academia SAP',
            'CertificadoSAP': 'Certificado SAP',
            'OtrasCertificaciones': 'Otras Certificaciones',
            'Postgrados': 'Postgrados',
            'Activo': 'Activo',
            'FechaRetiro': 'FechaRetiro',
            'Direccion': 'Direccion',
            'Departamento': 'Departamento',
            'DireccionAlterna': 'DirecccionAlterna',
            'Telefono1': 'Telefono1',
            'Telefono2': 'Telefono2',
            'Genero': 'Género',
            'EstadoCivil': 'Estado civil',
            'NumeroHijos': 'Número de hijos',
            'TarjetaProfesional': 'Tarjeta profesional',
            'RH': 'RH',
            'TipoContrato': 'Tipo de contrato',
            'FondoPension': 'Fondo de pensión',
            'EPS': 'EPS',
            'FondoCesantias': 'Fondo de cesantías',
            'CajaCompensacion': 'Caja de compensación',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['PerfilId'].empty_label = 'N/A'


class EmpleadoIndexFilterForm(forms.Form):
    """Filtro liviano para la lista de empleados (index)."""
    q = forms.CharField(
        required=False,
        label='Buscar (nombre o documento)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre o documento...'})
    )
    LineaId = forms.ModelChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label='Línea',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    CargoId = forms.ModelChoiceField(
        queryset=Cargos.objects.all(),
        required=False,
        label='Cargo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    PerfilId = forms.ModelChoiceField(
        queryset=Perfil.objects.all(),
        required=False,
        label='Perfil',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ModuloId = forms.ModelChoiceField(
        queryset=Modulo.objects.all(),
        required=False,
        label='Módulo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Activo = forms.ChoiceField(
        choices=[('', 'Todos'), ('1', 'Sí'), ('0', 'No')],
        required=False,
        label='Activo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['LineaId'].empty_label = 'Todas'
        self.fields['CargoId'].empty_label = 'Todos'
        self.fields['PerfilId'].empty_label = 'N/A / Todos'
        self.fields['ModuloId'].empty_label = 'Todos'


class EmpleadoFilterForm(forms.Form):
    Nombre = forms.ChoiceField(
        choices=[],  
        required=False, 
        label='Documento',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    CertificadoSAP = forms.ChoiceField(
        choices=[('', 'Seleccione'), ('1', 'SI'), ('0', 'NO')],
        required=False,
        label='Certificación',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    LineaId = forms.ModelChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ModuloId = forms.ChoiceField(
        choices=[],  
        required=False, 
        label='Módulo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Anio = forms.ChoiceField(
        choices=[],
        required=False,
        label='Año',  
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Mes = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    Cargo = forms.ChoiceField(
        choices=[],  # Se llenará dinámicamente en el __init__
        required=False,
        label='Cargo',  
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    PerfilId = forms.ModelChoiceField(
        queryset=Perfil.objects.all(),
        required=False,
        label="Perfil",
        widget=forms.Select(attrs={'class': 'form-control'})
    ) 
    Documento = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.all(),
        required=False,
        label="TipoDocumento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Activo = forms.ChoiceField(
        choices=[
            ('', 'Seleccione estado'),
            ('True', 'Sí'),
            ('False', 'No')
        ],
        required=False,
        label='Activo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Cliente = forms.ChoiceField(
        choices=[],  # Se llenará dinámicamente en el __init__
        required=False,
        label='Cliente',  
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        certificacion_seleccionada = kwargs.pop('certificacion_seleccionada', None)
        super(EmpleadoFilterForm, self).__init__(*args, **kwargs)

        ''' certificaciones = Empleado.objects.values_list('CertificadoSAP', flat=True).distinct()
        self.fields['CertificadoSAP'].choices = [('', 'Seleccione la certificación')] + [(empleado, empleado) for empleado in certificaciones]
        '''
        lineas = Linea.objects.values_list('LineaId', 'Linea').distinct()
        self.fields['LineaId'].choices = [('', 'Seleccione la línea')] + [(linea[0], linea[1]) for linea in lineas]

        empleados = Empleado.objects.values_list('Nombre', flat=True).distinct()
        self.fields['Nombre'].choices = [('', 'Seleccione el colaborador')] + [(empleado, empleado) for empleado in empleados]

        Modulo = Empleado.objects.values_list('ModuloId', flat=True).distinct()
        self.fields['ModuloId'].choices = [('', 'Seleccione el módulo')] + [(modulo, modulo) for modulo in Modulo]

        cargos = Cargos.objects.values_list('CargoId', 'Cargo').distinct()
        self.fields['Cargo'].choices = [('', 'Seleccione el cargo')] + [(cargo[0], cargo[1]) for cargo in cargos]
        
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [
        (str(year), str(year)) for year in range(2022, date.today().year + 1)
        ]
class HistorialCargosForm(forms.ModelForm):
    documentoId= forms.ModelChoiceField(
        queryset=Empleado.objects.all(),
        widget=forms.Select(attrs={
            'class':'form-control'
        }),
        label='Documento'
    )
    cargoId= forms.ModelChoiceField(
        queryset=Cargos.objects.all(),
        widget=forms.Select(attrs={
            'class':'form-control'
        }),
        label='Cargo'
    )
    class Meta:
        model = Historial_Cargos
        fields = '__all__'
        widgets = {
            'FechaInicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'FechaFin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {  
            'FechaInicio': 'Fecha de Inicio',
            'FechaFin': 'Fecha de Fin',
        }

class EmpleadosEstudiosForm(forms.ModelForm):
    documentoId=forms.ModelChoiceField(
        queryset=Empleado.objects.all(),
        widget=forms.Select(attrs={
            'class':'form-control'
        }),
        label='Documento'
    )
    class Meta:
        model = Empleados_Estudios
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el titulo'}),
            'institucion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la institucion'}),
            'fecha_Inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_Fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_Graduacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'titulo': 'Título',
            'institucion': 'Institución',
            'fecha_Inicio': 'Fecha de Inicio (opcional)',
            'fecha_Fin': 'Fecha de Fin (opcional)',
            'fecha_Graduacion': 'Fecha de Graduación',
        }
        help_texts = {
            'fecha_Inicio': 'Puede dejarse en blanco.',
            'fecha_Fin': 'Puede dejarse en blanco.',
        }

class HorasHabilesForm(forms.ModelForm):
    class Meta:
        model = Horas_Habiles
        fields = '__all__'
        widgets = {
            'Anio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el año'
            }),
            'Mes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el mes'
            }),
            'Dias_Habiles': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese los días hábiles'
            }),
            'Horas_Laborales': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese las horas laborales'
            }),
        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
            'Dias_Habiles': 'Días Hábiles',
            'Horas_Laborales': 'Horas Laborales',
        }

class Tarifa_ConsultoresForm(forms.ModelForm):

    monedaId = forms.ModelChoiceField(
        queryset=Moneda.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Moneda'
    )

    moduloId = forms.ModelChoiceField( 
        queryset=Modulo.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Módulo',
        to_field_name='ModuloId'
    )
    
    class Meta:
        model = Tarifa_Consultores
        fields = '__all__'
        widgets = {
            'documentoId': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione el documento'}),
            'anio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el año'}),
            'mes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el mes'}),
            'clienteID': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione el cliente'}),
            'valorHora': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor hora', 'step': '0.01'}),
            'valorDia': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor día', 'step': '0.01'}),
            'valorMes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor mes', 'step': '0.01'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor iva', 'step': '0.01'}),
            'rteFte': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor rtefte', 'step': '0.01'}),
            
        }
        labels = {
            'anio': 'Año',
            'mes': 'Mes',
            'valorHora': 'Valor Hora',
            'valorDia': 'Valor Día',
            'valorMes': 'Valor Mes',
            'iva': 'IVA',
            'rteFte': 'RteFte',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monedaId'].required = True  # Campo obligatorio
        self.fields['monedaId'].label_from_instance = lambda obj: obj.Nombre  # Mostrar solo el nombre de la moneda

    def clean(self):
        cleaned_data = super().clean()
        documentoId = cleaned_data.get('documentoId')
        anio = cleaned_data.get('anio')
        mes = cleaned_data.get('mes')
        clienteID = cleaned_data.get('clienteID')
        moduloId = cleaned_data.get('moduloId')
        print(moduloId)

        iva = cleaned_data.get('iva')
        rteFte = cleaned_data.get('rteFte')
        # Convertir valores en blanco a None
        if iva == '':
            cleaned_data['iva'] = None
        if rteFte == '':
            cleaned_data['rteFte'] = None

        if Tarifa_Consultores.objects.filter(
            documentoId=documentoId,
            anio=anio,
            mes=mes,
            clienteID=clienteID,
            moduloId=moduloId
        ).exists():
            raise ValidationError("Ya existe un registro con el mismo Documento, Año, Mes, Cliente y Módulo.")
        
        return cleaned_data

class MonedaForm(forms.ModelForm):
    class Meta:
        model = Moneda
        fields = '__all__'
        widgets = {
            'id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el id'}),
            'Nombre':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese nombre de la moneda'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese descripcion de la moneda'}),
        }
        labels = {
            'id': 'Id',
            'Nombre':'Nombre',
            'descripcion': 'Descripción',
        }
    def clean_Nombre(self):
        nombre = self.cleaned_data.get('Nombre')
        if Moneda.objects.filter(Nombre=nombre).exists():
            raise ValidationError('Ya existe una moneda con ese nombre')
        return nombre

class ClientesContratosForm(forms.ModelForm):

    monedaId = forms.ModelChoiceField(
        queryset=Moneda.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Moneda'
    )

    ClienteId = forms.ModelChoiceField(
        queryset=Clientes.objects.all(),  
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Cliente'
    )
    class Meta:
        model = ClientesContratos
        fields = '__all__'
        widgets = {
            'FechaInicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'FechaFin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Contrato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el contrato'}),
            'ContratoVigente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'OC_Facturar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Parafiscales': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'HorarioServicio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el horario de servicio'}),
            'FechaFacturacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la fecha de facturacion'}),
            'TipoFacturacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el tipo de facturacion'}),
            'Observaciones': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese las observaciones'}),
            'Polizas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'PolizasDesc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción de las poliza'}),
            'ContratoValor':  forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el Valor'}),
            'IncluyeIvaValor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ContratoDesc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción del contrato'}),
            'ServicioRemoto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'FechaInicio': 'Fecha de Inicio',
            'FechaFin': 'Fecha de Fin',
            'Contrato': 'Contrato',
            'ContratoVigente': 'Contrato Vigente',
            'OC_Facturar': 'OC Facturar',
            'Parafiscales': 'Parafiscales',
            'HorarioServicio': 'Horario de Servicio',
            'FechaFacturacion': 'Fecha de Facturacion',
            'TipoFacturacion': 'Tipo de Facturacion',
            'Observaciones': 'Observaciones',
            'Polizas': 'Polizas',
            'PolizasDesc': 'Descripción de las Polizas',
            'ContratoValor': 'Valor del Contrato',
            'IncluyeIvaValor': 'Incluye Iva Valor',
            'ContratoDesc': 'Descripción del Contrato',
            'ServicioRemoto': 'Servicio Remoto',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monedaId'].required = True  # Campo obligatorio
        self.fields['monedaId'].label_from_instance = lambda obj: obj.Nombre  # Mostrar solo el nombre de la moneda   

    def clean(self):
        cleaned_data = super().clean()
        ClienteId = cleaned_data.get('ClienteId')
        FechaInicio = cleaned_data.get('FechaInicio')

        if ClientesContratos.objects.filter(
            ClienteId=ClienteId,
            FechaInicio=FechaInicio
        ).exists():
            raise ValidationError(
                "Ya existe un registro con el mismo Cliente, Fecha de Inicio."
            )  
        return cleaned_data
    
class Tarifa_ClientesForm(forms.ModelForm):
    monedaId = forms.ModelChoiceField(
        queryset=Moneda.objects.all(),  # Relación directa con el modelo Consultores
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Moneda'
    )

    referenciaId= forms.ModelChoiceField(
        queryset=Referencia.objects.all(),
        widget=forms.Select(attrs={
            'class':'form-control'
        }),
        label='Referencia'
    )

    centrocostosId=forms.ModelChoiceField(
        queryset=CentrosCostos.objects.all(),
        widget=forms.Select(attrs={
            'class':'form-control'
        }),
        label='Centro de Costos'
    )

    class Meta:
        model = Tarifa_Clientes
        fields = '__all__'  
        widgets = {
            'clienteId': forms.Select(attrs={'class': 'form-control'}),
            'lineaId': forms.Select(attrs={'class': 'form-control'}),
            'moduloId': forms.Select(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el año'}),
            'mes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el mes'}),
            'valorHora': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor hora', 'step': '0.01'}),
            'valorDia': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor día', 'step': '0.01'}),
            'valorMes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor mes', 'step': '0.01'}),
            'bolsaMes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la cantidad del mes', 'step': '0.01'}),
            'valorBolsa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor bolsa', 'step': '0.01'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor IVA', 'step': '0.01'}),
            'sitioTrabajo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el sitio de trabajo'}),
        }
        labels = {
            'clienteId': 'Cliente',
            'lineaId': 'Línea',
            'moduloId': 'Módulo',
            'anio': 'Año',
            'mes': 'Mes',
            'ValorHora': 'Valor Hora',
            'ValorDia': 'Valor Día',
            'ValorMes': 'Valor Mes',
            'bolsaMes': 'Cantidad bolsa mes',
            'valorBolsa': 'valorBolsa',
            'iva': 'IVA',
            'SitioTrabajo': 'Sitio de Trabajo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monedaId'].required = True  # Campo obligatorio
        self.fields['monedaId'].label_from_instance = lambda obj: obj.Nombre  # Mostrar solo el nombre de la moneda
         # Mostrar solo el nombre de la moneda
    
    def clean(self):
        cleaned_data = super().clean()
        clienteId = cleaned_data.get('clienteId')
        lineaId = cleaned_data.get('lineaId')
        moduloId = cleaned_data.get('moduloId')
        anio = cleaned_data.get('anio')
        mes = cleaned_data.get('mes')   

        if Tarifa_Clientes.objects.filter(
            clienteId=clienteId,
            lineaId=lineaId,
            moduloId=moduloId,
            anio=anio,
            mes=mes
        ).exists():
            raise ValidationError("Ya existe un registro con el mismo Cliente, Línea, Modulo, Año y Mes.")
        return cleaned_data 
    
class FacturacionFilterForm(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=True,
        label='Año *Obligatorio*',  # Modificado aquí
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Mes = forms.ChoiceField(
        choices=[],
        required=True,
        label='Mes *Obligatorio*',  # Modificado aquí
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    ClienteId = forms.ModelChoiceField(
        queryset=Clientes.objects.all(), 
        required=False, 
        label='Cliente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    LineaId = forms.ModelChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    ModuloId = forms.ModelChoiceField(
        queryset=Modulo.objects.all(),
        required=False,
        label="Modulo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_anio()
        self.populate_mes()
        self.populate_cliente()
        self.populate_linea()

    def populate_anio(self):
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in range(2021, 2026)]

    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = [('', 'Seleccione el mes')] + meses
    
    def populate_cliente(self):
        clientes = Clientes.objects.values_list('ClienteId', 'Nombre_Cliente').distinct()
        self.fields['ClienteId'].choices = [('', 'Seleccione el cliente')] + list(clientes)

    def populate_linea(self):
        linea = Linea.objects.values_list('LineaId', 'Linea').distinct()
        self.fields['LineaId'].choices = [('', 'Seleccione la linea')] + list(linea)
        
class ConsultorFilterForm(forms.Form):
    Nombre = forms.ModelChoiceField(
        queryset=Consultores.objects.values_list('Nombre', flat=True).distinct(),
        required=False,
        label='Consultor',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    LineaId = forms.ModelChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ModuloId = forms.ChoiceField(
        choices=[],  
        required=False, 
        label='Módulo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Certificacion = forms.ChoiceField(
        choices=[('', 'Seleccione'), ('1', 'SI'), ('0', 'NO')],
        required=False,
        label='Certificación',  
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    PerfilId = forms.ModelChoiceField(
        queryset=Perfil.objects.all(),
        required=False,
        label="Perfil",
        widget=forms.Select(attrs={'class': 'form-control'})
    ) 
    Estado = forms.ChoiceField(
        choices=[('', 'Seleccione'), ('1', 'Activo'), ('0', 'Inactivo')],
        required=False,
        label='Estado',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_nombre()
        self.populate_modulo()
        self.populate_linea()
        self.populate_perfil()

    def populate_nombre(self):
        consultores = Consultores.objects.values_list('Documento', 'Nombre', 'Empresa').distinct()
        self.fields['Nombre'].choices = [('', 'Seleccione el Consultor')] + [
        (doc, f"{nombre} - {empresa}") for doc, nombre, empresa in consultores
    ]
        
    def populate_modulo(self):
        modulos = Modulo.objects.values_list('ModuloId', 'Modulo').distinct()
        self.fields['ModuloId'].choices = [('', 'Seleccione el Módulo')] + list(modulos)

    def populate_linea(self):
        # Si ModuloId necesita opciones dinámicas, añade lógica aquí.
        linea = Linea.objects.values_list('LineaId', 'Linea').distinct()  # Ajusta según tus modelos
        self.fields['LineaId'].choices = [('', 'Seleccione la linea')] + list(linea)

    def populate_perfil(self):
        # Si ModuloId necesita opciones dinámicas, añade lógica aquí.
        perfil = Perfil.objects.values_list('PerfilId', 'Perfil').distinct()  # Ajusta según tus modelos
        self.fields['PerfilId'].choices = [('', 'Seleccione el perfil')] + list(perfil)
    
class EstudiosFilterForm(forms.Form):
    Nombre = forms.ChoiceField(
        choices=[],  
        required=False, 
        label='Colaborador',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    LineaId = forms.ModelChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Cargo = forms.ChoiceField(
        choices=[], 
        required=False,
        label='Cargo',  
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super(EstudiosFilterForm, self).__init__(*args, **kwargs)

        empleados = Empleado.objects.values_list('Nombre', flat=True).distinct()
        self.fields['Nombre'].choices = [('', 'Seleccione el colaborador')] + [(empleado, empleado) for empleado in empleados]

        lineas = Linea.objects.values_list('LineaId', 'Linea').distinct()
        self.fields['LineaId'].choices = [('', 'Seleccione la línea')] + [(linea[0], linea[1]) for linea in lineas]
        
        cargos = Cargos.objects.values_list('CargoId', 'Cargo').distinct()
        self.fields['Cargo'].choices = [('', 'Seleccione el cargo')] + [(cargo[0], cargo[1]) for cargo in cargos]


class ReferenciaForm(forms.ModelForm):
    class Meta:
        model = Referencia
        fields = '__all__'
        widgets = {
            'codigoReferencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el codigo'}),
            'descripcionReferencia': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripcion'}),
        }
        labels = {
            'codigoReferencia': 'Codigo',
            'descripcionReferencia': 'Descripcion',
        }

class CentrosCostosForm(forms.ModelForm):
    class Meta:
        model = CentrosCostos
        fields = '__all__'
        widgets = {
            'codigoCeCo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el codigo'}),
            'descripcionCeCo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripcion'}),
        }
        labels = {
            'codigoCeCo': 'Codigo',
            'descripcionCeCo': 'Descripcion',
        }


class Ind_Operatividad_FilterForm(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=True,
        label='Año *Obligatorio*', # Modificado aquí
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    Mes = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Mes',
        widget=forms.CheckboxSelectMultiple()
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_anio()
        self.populate_mes()

    def populate_anio(self):
        years = Horas_Habiles.objects.values_list('Anio', flat=True).distinct().order_by('Anio')
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in years]

    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = meses

class Ind_Totales_FilterForm(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=True,
        label='Año *Obligatorio*', # Modificado aquí
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    Mes = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Mes',
        widget=forms.CheckboxSelectMultiple()
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.CheckboxSelectMultiple()
    )

    ClienteId = forms.ModelMultipleChoiceField(
        queryset=Clientes.objects.only('DocumentoId', 'Nombre_Cliente'),
        required=False,
        label="Cliente",
        widget=forms.CheckboxSelectMultiple() 
    )   
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_anio()
        self.populate_mes()
        # Personalizar cómo se muestran los clientes
        self.fields['ClienteId'].label_from_instance = lambda obj: f"{obj.Nombre_Cliente} - {obj.DocumentoId}"

    def populate_anio(self):
        years = Horas_Habiles.objects.values_list('Anio', flat=True).distinct().order_by('Anio')
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in years]

    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = meses
    

class TarifaConsultorFilterForm(forms.Form):
    Nombre = forms.ModelChoiceField(
        queryset=Consultores.objects.values_list('Nombre', flat=True).distinct(),
        required=False,
        label='Consultor',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    LineaId = forms.ModelChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    anio = forms.MultipleChoiceField(
        choices=[],  
        required=True, 
        label='Año *Obligatorio*',
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_nombre()
        self.populate_linea()
        self.populate_anio()

    def populate_nombre(self):
        consultores = Consultores.objects.values_list('Documento', 'Nombre', 'Empresa').distinct()
        self.fields['Nombre'].choices = [('', 'Seleccione el Consultor')] + [
        (doc, f"{nombre} - {empresa}") for doc, nombre, empresa in consultores
    ]
        
    def populate_linea(self):
        # Si ModuloId necesita opciones dinámicas, añade lógica aquí.
        linea = Linea.objects.values_list('LineaId', 'Linea').distinct()  # Ajusta según tus modelos
        self.fields['LineaId'].choices = [('', 'Seleccione la linea')] + list(linea)

    def populate_anio(self):
        anios = Tarifa_Consultores.objects.values_list('anio', flat=True).distinct()
        self.fields['anio'].choices = [(anio, anio) for anio in anios]


class ClienteFilterForm(forms.Form):
    Nombre_Cliente = forms.ModelChoiceField(
        queryset=Clientes.objects.only('Nombre_Cliente'),
        required=False,
        label='Cliente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Activo = forms.ChoiceField(
        choices=[
            ('', 'Seleccione estado'),
            ('True', 'Sí'),
            ('False', 'No')
        ],
        required=False,
        label='Activo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Pais = forms.ChoiceField(
        choices=[('', 'Seleccione un país')] + [(p, p) for p in Clientes.objects.values_list('Pais', flat=True).distinct()],
        required=False,
        label='Pais',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Ciudad = forms.ChoiceField(
        choices=[('', 'Seleccione una ciudad')] + [(c, c) for c in Clientes.objects.values_list('Ciudad', flat=True).distinct()],
        required=False,
        label='Ciudad',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    TipoCliente = forms.ChoiceField(
        choices=[('', 'Seleccione un tipo de cliente')] + [(t, t) for t in Clientes.objects.values_list('TipoCliente', flat=True).distinct()],
        required=False,
        label='Tipo Cliente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Nacional = forms.ChoiceField(
        choices=[
            ('', 'Seleccione estado'),
            ('True', 'Sí'),
            ('False', 'No')
        ],
        required=False,
        label='Nacional',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_choices()

    def populate_choices(self):    
        self.fields['Nombre_Cliente'].queryset = Clientes.objects.all().order_by('Nombre_Cliente')
        self.fields['Nombre_Cliente'].label_from_instance = lambda obj: obj.Nombre_Cliente

class InformeFacturacionForm(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=False,
        label='Año',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.CheckboxSelectMultiple()
    )

    ClienteId = forms.ModelMultipleChoiceField(
        queryset=Clientes.objects.only('DocumentoId', 'Nombre_Cliente'),
        required=False,
        label="Cliente",
        widget=forms.CheckboxSelectMultiple() 
    )   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Llenar el campo de años dinámicamente
        years = FacturacionClientes.objects.values_list('Anio', flat=True).distinct().order_by('-Anio')
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(year, year) for year in years]
        
        # Personalizar cómo se muestran los clientes
        self.fields['ClienteId'].label_from_instance = lambda obj: f"{obj.Nombre_Cliente}"

        

class TarifaClienteFilterForm(forms.Form):
    Nombre_Cliente = forms.ModelChoiceField(
        queryset=Clientes.objects.values_list('Nombre_Cliente', flat=True).distinct(),
        required=False,
        label='Cliente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    LineaId = forms.ModelChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ModuloId = forms.ChoiceField(
        choices=[],  
        required=False, 
        label='Módulo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Activo = forms.ChoiceField(
        choices=[('', 'Seleccione'), ('1', 'Activo'), ('0', 'Inactivo')],
        required=False,
        label='Estado',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    anio = forms.MultipleChoiceField(
        choices=[],  
        required=False, 
        label='Año',
        widget=forms.CheckboxSelectMultiple()
    )
   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_nombre()
        self.populate_linea()
        self.populate_modulo()
        self.populate_anio()

    def populate_nombre(self):
        clientes = Clientes.objects.values_list('ClienteId', 'Nombre_Cliente').distinct()
        self.fields['Nombre_Cliente'].choices = [('', 'Seleccione el Cliente')] + list(clientes)
        
    def populate_linea(self):
        # Si ModuloId necesita opciones dinámicas, añade lógica aquí.
        linea = Linea.objects.values_list('LineaId', 'Linea').distinct()  # Ajusta según tus modelos
        self.fields['LineaId'].choices = [('', 'Seleccione la linea')] + list(linea)

    def populate_modulo(self):
        modulos = Modulo.objects.values_list('ModuloId', 'Modulo').distinct()
        self.fields['ModuloId'].choices = [('', 'Seleccione el Módulo')] + list(modulos)


    def populate_anio(self):
        anios = Tarifa_Clientes.objects.values_list('anio', flat=True).distinct()
        self.fields['anio'].choices = [(anio, anio) for anio in anios]

class HistorialCargosFilterForm(forms.Form):
    Empleado = forms.ModelMultipleChoiceField(
        queryset=Empleado.objects.all(),
        required=False,
        label="Empleado",
        widget=forms.CheckboxSelectMultiple()
    )

    Linea = forms.ModelMultipleChoiceField( 
        queryset=Linea.objects.all(),
        required=False,
        label="Linea",
        widget=forms.CheckboxSelectMultiple()
    )

    Cargo = forms.ModelMultipleChoiceField(
        queryset=Cargos.objects.all(),
        required=False,
        label="Cargo",
        widget=forms.CheckboxSelectMultiple()
    )
    def __init__(self, *args, **kwargs):
        super(HistorialCargosFilterForm, self).__init__(*args, **kwargs)

        empleados = Empleado.objects.values_list('Documento', 'Nombre').distinct()
        self.fields['Empleado'].choices = [('', 'Seleccione el empleado')] + [(empleado[0], empleado[1]) for empleado in empleados]

        lineas = Linea.objects.values_list('LineaId', 'Linea').distinct()
        self.fields['Linea'].choices = [('', 'Seleccione la línea')] + [(linea[0], linea[1]) for linea in lineas]

        cargos = Cargos.objects.values_list('CargoId', 'Cargo').distinct()
        self.fields['Cargo'].choices = [('', 'Seleccione el cargo')] + [(cargo[0], cargo[1]) for cargo in cargos]

class ClientesContratosFilterForm(forms.Form):
    Nombre_Cliente = forms.ModelChoiceField(
        queryset=Clientes.objects.values_list('Nombre_Cliente', flat=True).distinct(),
        required=False,
        label='Cliente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    FechaInicio = forms.DateField(
        required=False,
        label='Fecha Inicio',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    ContratoVigente = forms.ChoiceField(
        choices=[('', 'Seleccione'), ('True', 'Sí'), ('False', 'No')],
        required=False,
        label='Contrato Vigente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_nombre()
    
    def populate_nombre(self):
        clientes = Clientes.objects.values_list('ClienteId', 'Nombre_Cliente').distinct()
        self.fields['Nombre_Cliente'].choices = [('', 'Seleccione el Cliente')] + list(clientes)

class TotalesPorMesFilterForm(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=False,
        label='Año',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.CheckboxSelectMultiple()
    )

    Mes = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Mes',
        widget=forms.CheckboxSelectMultiple()
    )
    Consultor = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Consultor',
        widget=forms.CheckboxSelectMultiple()
    )  
   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_mes()

        # Llenar el campo de años dinámicamente
        years = Facturacion_Consultores.objects.values_list('Anio', flat=True).distinct().order_by('-Anio')
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(year, year) for year in years]

        consultores = Consultores.objects.values_list('Documento', 'Nombre', 'Empresa')
        self.fields['Consultor'].choices = [(c[0], f"{c[1]} - {c[2]}") for c in consultores]
        
    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = [('', 'Seleccione el mes')] + meses

class TotalesPorMesFilterForm2(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=False,
        label='Año',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.CheckboxSelectMultiple()
    )

    Mes = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Mes',
        widget=forms.CheckboxSelectMultiple()
    )
    Consultor = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Consultor',
        widget=forms.CheckboxSelectMultiple()
    )  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_mes()
        
        consultores = Consultores.objects.values_list('Documento', 'Nombre')
        self.fields['Consultor'].choices = [(c[0], c[1]) for c in consultores]

        # Llenar el campo de años dinámicamente
        years = Facturacion_Consultores.objects.values_list('Anio', flat=True).distinct().order_by('-Anio')
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(year, year) for year in years]

    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = [('', 'Seleccione el mes')] + meses
        
class ContratosOtrosSiForm(forms.ModelForm):

    monedaId = forms.ModelChoiceField(
        queryset=Moneda.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Moneda'
    )

    ClienteId = forms.ModelChoiceField(
        queryset=Clientes.objects.all(),  
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Cliente'
    )

    Contrato = forms.CharField(
    max_length=50,
    required=True,
    widget=forms.Select(attrs={'class': 'form-control'}),
    label='Contrato *Obligatorio*' # Modificado aquí
)

    class Meta:
        model = ContratosOtrosSi
        fields = '__all__'
        widgets = {
            'FechaInicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'FechaFin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'NumeroOtroSi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el Numero de Otro Si'}),
            'ValorOtroSi': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el Valor'}),
            'ValorIncluyeIva': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Polizas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'PolizasDesc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción de las poliza'}),
            'FirmadoFlag': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'FirmadoCliente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'FechaInicio': 'Fecha de Inicio',
            'FechaFin': 'Fecha de Fin',
            'NumeroOtroSi': 'Numero de Otro Si',
            'ValorOtroSi': 'Valor Otro Si',
            'ValorIncluyeIva': 'Valor Incluye Iva',
            'Polizas': 'Polizas',
            'PolizasDesc': 'Descripción de las Polizas',
            'FirmadoFlag': 'Firmado Flag',
            'FirmadoCliente': 'Firmado Cliente',
        }

    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        super().__init__(*args, **kwargs)
        if cliente_id:
            contratos = ClientesContratos.objects.filter(ClienteId=cliente_id, ContratoVigente=True)
            self.fields['Contrato'].widget.choices = [
                (c.Contrato, c.Contrato) for c in contratos]
        self.fields['monedaId'].required = True  # Campo obligatorio
        self.fields['monedaId'].label_from_instance = lambda obj: obj.Nombre  # Mostrar solo el nombre de la moneda

    def clean(self):
        cleaned_data = super().clean()
        ClienteId = cleaned_data.get('ClienteId')
        FechaInicio = cleaned_data.get('FechaInicio')

        if ContratosOtrosSi.objects.filter(
            ClienteId=ClienteId,
            FechaInicio=FechaInicio
        ).exists():
            raise ValidationError(
                "Ya existe un registro con el mismo Cliente, Fecha de Inicio."
            )  
        return cleaned_data
    
class OtrosSiFilterForm(forms.Form):
    Nombre_Cliente = forms.ModelChoiceField(
        queryset=Clientes.objects.values_list('Nombre_Cliente', flat=True).distinct(),
        required=False,
        label='Cliente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    FechaInicio = forms.DateField(
        required=False,
        label='Fecha Inicio',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    Contrato = forms.ChoiceField(
        required=False,
        label='Contrato',
        choices=[],  # Se llenará dinámicamente en __init__
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ContratoVigente = forms.ChoiceField(
        choices=[('', 'Seleccione'), ('True', 'Sí'), ('False', 'No')],
        required=False,
        label='Contrato Vigente',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_nombre()

        contrato_actual = self.data.get('Contrato') or self.initial.get('Contrato')
        cliente_nombre = self.data.get('Nombre_Cliente') or self.initial.get('Nombre_Cliente')

        contratos_choices = [('', 'Seleccione un Contrato')]

        if cliente_nombre:
            self.fields['Nombre_Cliente'].initial = cliente_nombre
            cliente = Clientes.objects.filter(Nombre_Cliente=cliente_nombre).first()
            if cliente:
                contratos = ContratosOtrosSi.objects.filter(
                    ClienteId=cliente.ClienteId
                ).values_list('Contrato', flat=True).distinct()
                contratos_choices += [(c, c) for c in contratos]

        # Asegurar que el contrato actual esté disponible
        if contrato_actual and (contrato_actual, contrato_actual) not in contratos_choices:
            contratos_choices.append((contrato_actual, contrato_actual))

        self.fields['Contrato'].choices = contratos_choices

        # Si el contrato está en choices, seleccionarlo
        if contrato_actual:
            self.fields['Contrato'].initial = contrato_actual
        
        if self.data.get('ContratoVigente') in ['True', 'False']:
            self.fields['ContratoVigente'].initial = self.data['ContratoVigente']
    
    def populate_nombre(self):
        clientes = Clientes.objects.values_list('ClienteId', 'Nombre_Cliente').distinct()
        self.fields['Nombre_Cliente'].choices = [('', 'Seleccione el Cliente')] + list(clientes)

class inforTiempoEmpleadosFilterForm(forms.Form):
    documento = forms.ModelMultipleChoiceField(
        queryset=Consultores.objects.all(),
        required=False,
        label='Documento',
        widget=forms.CheckboxSelectMultiple(),
        to_field_name='Documento',
    )

    Anio = forms.ChoiceField(
        choices=[],
        required=False,
        label='Año',
        widget=forms.Select(attrs={'class': 'form-control'})

    )

    Mes = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Mes',
        widget=forms.CheckboxSelectMultiple()
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Linea",
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_mes()

        # Personalizar cómo se muestra cada consultor
        self.fields['documento'].label_from_instance = lambda obj: f'{obj.Nombre} -{obj.Empresa}'

        # Llenar dinámicamente el campo de años
        years = Tiempos_Cliente.objects.values_list('Anio', flat=True).distinct().order_by('-Anio')
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(year, year) for year in years]

    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = meses

class CertificacionesFilterForm(forms.Form):
    Nombre = forms.CharField(
        label='Nombre del Empleado',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    LineaId = forms.ModelChoiceField(
        queryset=Linea.objects.all(),
        label='Línea',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    Certificacion = forms.ModelChoiceField(
        queryset=Certificacion.objects.all(),
        label='Certificación',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ActividadPagareForm(forms.ModelForm):
    class Meta:
        model = ActividadPagare
        fields = ['Act_PagareId', 'Descripcion_Act']  # Incluir el código
        labels = {
            'Act_PagareId': 'Código',
            'Descripcion_Act': 'Descripción'
        }
        widgets = {
            'Act_PagareId': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1001'
            }),
            'Descripcion_Act': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la actividad'
            })
        }

class PagareFilterForm(forms.Form):
    documento = forms.ModelMultipleChoiceField(
        queryset=Empleado.objects.filter(Activo=True),  # Filtra solo empleados activos
        required=False,
        label='Empleado',
        widget=forms.CheckboxSelectMultiple(),
        to_field_name='Documento',  # Campo que se usará para identificar al empleado
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar cómo se muestra cada consultor
        self.fields['documento'].label_from_instance = lambda obj: f'{obj.Nombre} - {obj.Documento}'

class EmpleadoConPagareFilterForm(forms.Form):
    empleados_con_pagare = forms.ModelMultipleChoiceField(
        queryset=Empleado.objects.filter(
            Documento__in=Pagare.objects.values_list('Documento', flat=True)
        ).distinct().order_by('Nombre'),
        required=False,
        label='Empleados con pagaré',
        widget=forms.CheckboxSelectMultiple(),
        to_field_name='Documento',
    )

    Anio = forms.ChoiceField(
        choices=[],
        required=False,
        label='Año',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.CheckboxSelectMultiple()
    )

    tipo_pagare = forms.ModelMultipleChoiceField(
        queryset=TipoPagare.objects.all(),
        required=False,
        label='Tipo de pagaré',
        widget=forms.CheckboxSelectMultiple(),
        to_field_name='Tipo_PagareId',
    )

    estado_pagare = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('proceso', 'Proceso'),
            ('terminado', 'Terminado'),
            ('cancelado', 'Cancelado'),
        ],
        required=False,
        label='Estado del pagaré',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['empleados_con_pagare'].label_from_instance = (
            lambda obj: f'{obj.Nombre}<br><span class="text-muted small">{obj.Documento}</span>'
        )

        current_year = datetime.now().year
        available_years = range(2023, current_year + 1)
        self.fields['Anio'].choices = [('', 'Todos')] + [(year, year) for year in available_years]

class Ind_Facturacion_FilterForm(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=True,
        label='Año *Obligatorio*', # Corregido aquí
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    Mes = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Mes',
        widget=forms.CheckboxSelectMultiple()
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_anio()
        self.populate_mes()

    def populate_anio(self):
        years = Horas_Habiles.objects.values_list('Anio', flat=True).distinct().order_by('Anio')
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in years]

    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'),
            ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
            ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Septiembre'),
            ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = meses

class FacturacionConsultoresFilterForm(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=True,
        label='Año *Obligatorio*',  # Modificado aquí
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Mes = forms.ChoiceField(
        choices=[],
        required=True,
        label='Mes *Obligatorio*',  # Modificado aquí
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Mes_Cobro = forms.MultipleChoiceField(
        choices=[],
        required=True,
        label="Mes a Cobrar *Obligatorio*",
        widget=forms.CheckboxSelectMultiple()
    )

    LineaId = forms.ChoiceField(
        choices=[],
        required=False,
        label="Línea",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Consultor = forms.ChoiceField(
        choices=[],
        required=False, 
        label='Consultor',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_anio()
        self.populate_mes()
        self.populate_mes_cobro()
        self.populate_consultor()
        self.populate_linea()

    def populate_anio(self):
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in range(2021, 2026)]

    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = [('', 'Seleccione el mes')] + meses
    
    def populate_mes_cobro(self):
        meses2 = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes_Cobro'].choices = meses2

    def populate_consultor(self):
        consultores = Consultores.objects.values_list('Documento', 'Nombre', 'Empresa').distinct()
        self.fields['Consultor'].choices = [('', 'Seleccione el Consultor')] + [(doc, f"{nombre} - {empresa}") for doc, nombre, empresa  in consultores]

    def populate_linea(self):
        lineas = Linea.objects.values_list('LineaId', 'Linea').distinct()
        self.fields['LineaId'].choices = [('', 'Seleccione la línea')] + [(lid, nombre) for lid, nombre in lineas]

class FacturacionConsultoresDetalleFilterForm(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=False,
        label='Año',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    Mes = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Mes',
        widget=forms.CheckboxSelectMultiple()
    )

    Consultor = forms.ModelMultipleChoiceField(
        queryset=Consultores.objects.all(),
        required=False,
        label='Consultor',
        widget=forms.CheckboxSelectMultiple(),
        to_field_name='Documento',
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label='Línea',
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_anio()
        self.populate_mes()
        # Personalizar cómo se muestran los consultores
        self.fields['Consultor'].label_from_instance = lambda obj: f"{obj.Nombre} - {obj.Empresa}"

    def populate_anio(self):
        years = Facturacion_Consultores.objects.values_list('Anio', flat=True).distinct().order_by('-Anio')
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in years]

    def populate_mes(self):
        meses = [
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ]
        self.fields['Mes'].choices = meses

class FacturacionClientesFilterForm(forms.Form):
    Anio = forms.ChoiceField(
        choices=[],
        required=True,  # ✅ ahora es obligatorio
        label="Año",
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debes seleccionar un año."},
    )

    LineaId = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        required=False,
        label="Línea",
        widget=forms.CheckboxSelectMultiple(),
    )

    Mes = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label="Mes",
        widget=forms.CheckboxSelectMultiple(),
    )

    Ceco = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label="Ceco",
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_anio()  # ✅ primero anio
        self.populate_mes()
        self.populate_ceco()

    def populate_anio(self):
        years = (
            FacturacionClientes.objects.values_list("Anio", flat=True)
            .distinct()
            .order_by("-Anio")
        )

        # ✅ Sin opción vacía: fuerza selección real
        self.fields["Anio"].choices = [(str(year), str(year)) for year in years]

    def populate_ceco(self):
        # Obtener valores únicos de Ceco, excluyendo vacíos y nulos
        cecos_facturas = (
            FacturacionClientes.objects.exclude(Ceco__isnull=True)
            .exclude(Ceco__exact="")
            .values_list("Ceco", flat=True)
            .distinct()
        )

        cecos_validos = CentrosCostos.objects.filter(
            codigoCeCo__in=cecos_facturas
        ).order_by("codigoCeCo")

        self.fields["Ceco"].choices = [
            (str(ceco.codigoCeCo), f"{ceco.codigoCeCo}") for ceco in cecos_validos
        ]

    def populate_mes(self):
        meses = [
            ("1", "Enero"), ("2", "Febrero"), ("3", "Marzo"), ("4", "Abril"),
            ("5", "Mayo"), ("6", "Junio"), ("7", "Julio"), ("8", "Agosto"),
            ("9", "Septiembre"), ("10", "Octubre"), ("11", "Noviembre"), ("12", "Diciembre"),
        ]
        self.fields["Mes"].choices = meses

    def clean_Anio(self):
        """
        ✅ Seguridad extra: si por alguna razón llega '' o None, falla.
        """
        anio = self.cleaned_data.get("Anio")
        if not anio or str(anio).strip() == "":
            raise forms.ValidationError("Debes seleccionar un año.")
        return anio  

class TipoPagareForm(forms.ModelForm):
    class Meta:
        model = TipoPagare
        fields = ['Tipo_PagareId', 'Desc_Tipo_Pagare']
        widgets = {
            'Desc_Tipo_Pagare': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción del tipo de pagaré'}),
        }
        labels = {
            'Desc_Tipo_Pagare': 'Descripción del Tipo de Pagaré',
        }

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserRole
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que todos los campos de permisos sean checkboxes
        for field_name, field in self.fields.items():
            if field_name.startswith('can_'):
                field.widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
                # Mejorar las etiquetas
                field.label = self.get_permission_label(field_name)
    
    def get_permission_label(self, field_name):
        """Convierte nombres de campos en etiquetas legibles"""
        labels = {
            # Permisos de Administración
            'can_manage_users': 'Gestionar Usuarios',
            'can_manage_roles': 'Gestionar Roles',
            
            # Maestros
            'can_manage_actividades_pagares': 'Gestionar Actividades Pagarés',
            'can_manage_cargos': 'Gestionar Cargos',
            'can_manage_certificacion': 'Gestionar Certificación',
            'can_manage_clientes': 'Gestionar Clientes',
            'can_manage_conceptos': 'Gestionar Conceptos',
            'can_manage_consultores': 'Gestionar Consultores',
            'can_manage_contactos': 'Gestionar Contactos',
            'can_manage_costos_indirectos': 'Gestionar Costos Indirectos',
            'can_manage_centros_costos': 'Gestionar Centros de Costos',
            'can_manage_empleados': 'Gestionar Empleados',
            'can_manage_empleados_estudios': 'Gestionar Estudios de Empleados',
            'can_manage_gastos': 'Gestionar Gastos',
            'can_manage_horas_habiles': 'Gestionar Horas Hábiles',
            'can_manage_ind': 'Gestionar IND',
            'can_manage_ipc': 'Gestionar IPC',
            'can_manage_linea': 'Gestionar Línea',
            'can_manage_linea_cliente_centrocostos': 'Gestionar Relación Línea - Cliente - CeCo',
            'can_manage_modulo': 'Gestionar Módulo',
            'can_manage_moneda': 'Gestionar Moneda',
            'can_manage_perfil': 'Gestionar Perfil',
            'can_manage_referencias': 'Gestionar Referencias',
            'can_manage_tipo_documento': 'Gestionar Tipo Documento',
            'can_manage_tipos_contactos': 'Gestionar Tipos de Contactos',
            'can_manage_tipo_pagare': 'Gestionar Tipo Pagaré',
            
            # Movimientos
            'can_manage_clientes_contratos': 'Gestionar Contratos de Clientes',
            'can_manage_contratos_otros_si': 'Gestionar Contratos Otros Sí',
            'can_manage_pagare': 'Gestionar Pagarés',
            'can_manage_detalle_certificacion': 'Gestionar Detalle Certificación',
            'can_manage_detalle_costos_indirectos': 'Gestionar Detalle Costos Indirectos',
            'can_manage_detalle_gastos': 'Gestionar Detalle Gastos',
            'can_manage_historial_cargos': 'Gestionar Historial de Cargos',
            'can_manage_nomina': 'Gestionar Nómina',
            'can_manage_registro_tiempos': 'Gestionar Registro de Tiempos',
            'can_manage_tarifa_clientes': 'Gestionar Tarifa Clientes',
            'can_manage_tarifa_consultores': 'Gestionar Tarifa Consultores',
            'can_manage_total_costos_indirectos': 'Gestionar Total Costos Indirectos',
            'can_manage_total_gastos': 'Gestionar Total Gastos',
            'can_manage_clientes_factura': 'Gestionar Facturación Clientes',
            'can_manage_facturacion_consultores': 'Gestionar Facturación Consultores',
            
            # Informes
            'can_view_informe_certificacion': 'Ver Informe Certificación',
            'can_view_informe_empleado': 'Ver Informe Empleado',
            'can_view_informe_salarios': 'Ver Informe Salarios',
            'can_view_informe_estudios': 'Ver Informe Estudios',
            'can_view_informe_consultores': 'Ver Informe Consultores',
            'can_view_informe_tarifas_consultores': 'Ver Informe Tarifas Consultores',
            'can_view_informe_facturacion': 'Ver Informe Facturación',
            'can_view_informe_historial_cargos': 'Ver Informe Historial Cargos',
            'can_view_informe_tarifas_clientes': 'Ver Informe Tarifas Clientes',
            'can_view_informe_tiempos_consultores': 'Ver Informe Tiempos Consultores',
            'can_view_informe_clientes': 'Ver Informe Clientes',
            'can_view_informe_clientes_contratos': 'Ver Informe Contratos Clientes',
            'can_view_informe_otros_si': 'Ver Informe Otros Sí',
            'can_view_informe_pagares': 'Ver Informe Pagarés',
            'can_view_informe_facturacion_consultores': 'Ver Informe Facturación Consultores',
            'can_view_informe_serv_consultor': 'Ver Informe Servicios Consultor',
            'can_view_informe_facturacion_centrocostos': 'Ver Informe Facturación Centros Costos',
            'can_view_informe_detalle_facturacion_consultores': 'Ver Informe Detalle Facturación Consultores',
            
            # Indicadores
            'can_view_indicadores_operatividad': 'Ver Indicadores Operatividad',
            'can_view_indicadores_totales': 'Ver Indicadores Totales',
            'can_view_indicadores_facturacion': 'Ver Indicadores Facturación',
            'can_view_indicadores_margen_cliente': 'Ver Indicadores Margen Cliente',
        }
        return labels.get(field_name, field_name.replace('_', ' ').title())

class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Si estamos editando, excluimos al usuario actual
        if self.instance.pk:
            if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ya existe un usuario con ese nombre de usuario.")
        # Para creación nueva
        elif CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre de usuario.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Misma lógica para email
        if self.instance.pk:
            if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ya existe un usuario con ese email.")
        elif CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese email.")
        return email

class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre de usuario.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario con ese email.")
        return email

class LineaClienteCentroCostosForm(forms.ModelForm):
    class Meta:
        model = LineaClienteCentroCostos
        fields = ['linea', 'cliente', 'modulo', 'centro_costo']
        widgets = {
            'linea': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'modulo': forms.Select(attrs={'class': 'form-select'}),
            'centro_costo': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'linea': 'Línea',
            'cliente': 'Cliente',
            'modulo': 'Módulo',
            'centro_costo': 'Centro de Costos',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['linea'].queryset = Linea.objects.all().order_by('Linea')
        self.fields['cliente'].queryset = Clientes.objects.all().order_by('Nombre_Cliente')

        # Ajusta el order_by si tu campo se llama distinto
        try:
            self.fields['modulo'].queryset = Modulo.objects.all().order_by('Modulo')
        except Exception:
            self.fields['modulo'].queryset = Modulo.objects.all()

        self.fields['centro_costo'].queryset = CentrosCostos.objects.all().order_by('codigoCeCo')
