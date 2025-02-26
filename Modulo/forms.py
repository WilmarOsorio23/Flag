from django import forms
from .models import FacturacionClientes, Horas_Habiles, Modulo, IPC, IND, Linea, Perfil, TipoDocumento, Clientes, Consultores, Certificacion, Costos_Indirectos
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
from .models import Tarifa_Clientes
from .models import Referencia
from .models import CentrosCostos

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
    """
    class Meta:
        model = Clientes
        fields = [
            'TipoDocumentoID', 'DocumentoId', 'Nombre_Cliente', 'Activo', 
            'Fecha_Inicio', 'Fecha_Retiro', 'Direccion', 'Telefono', 
            'CorreoElectronico', 'BuzonFacturacion', 'TipoCliente', 
            'Ciudad', 'Departamento', 'Pais', 'ContactoID'
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
            'Direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la dirección'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'Cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el cargo'}),
        }

        labels ={
            'Nombre': 'Nombre',
            'Telefono': 'Teléfono',
            'Direccion': 'Dirección',  
            'activo': 'Activo',
            'Cargo':'Cargo',
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
        label='Año (Obligatorio)',  
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Mes = forms.ChoiceField(
        choices=[],
        required=True,
        label='Mes (Obligatorio)',  
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
            'Total': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el Total'
            }),
        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
            'Total': 'Total',
        }

class Total_Costos_IndirectosForm(forms.ModelForm):
    class Meta:
        model = Total_Costos_Indirectos
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
            'Total': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el Total'
            }),
        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
            'Total': 'Total',
        }

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
        }   
        labels = {
            'TipoDocumento': 'Tipo de Documento',
            'Documento': 'Documento',
            'Nombre': 'Nombre Completo',
            'FechaNacimiento': 'Fecha de Nacimiento',
            'FechaIngreso': 'Fecha de Ingreso',
            'FechaOperacion': 'Fecha de Operación',
            'ModuloId': 'Módulo',
            'PerfilId': 'Perfil',
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
            'Telefono2':'Telefono2',
        }

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
        
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in range(2022, 2025)]

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
            'titulo': 'Titulo',
            'institucion': 'Institucion',
            'fecha_Inicio': 'Fecha de Inicio',
            'fecha_Fin': 'Fecha de Fin',
            'fecha_Graduacion': 'Fecha de Graduacion',
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
            
        }
        labels = {
            'anio': 'Año',
            'mes': 'Mes',
            'valorHora': 'Valor Hora',
            'valorDia': 'Valor Día',
            'valorMes': 'Valor Mes',
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

        if Tarifa_Consultores.objects.filter(
            documentoId=documentoId,
            anio=anio,
            mes=mes,
            clienteID=clienteID
        ).exists():
            raise ValidationError(
                "Ya existe un registro con el mismo Documento, Año, Mes y Cliente."
            )
        
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
        }

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
        label='Año',  
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Mes = forms.ChoiceField(
        choices=[],
        required=False,
        label='Mes',  
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
        consultores = Consultores.objects.values_list('Documento', 'Nombre').distinct()
        self.fields['Nombre'].choices = [('', 'Seleccione el Consultor')] + list(consultores)
        
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
        label='Año',
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
        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in range(2022, 2026)]

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
        required=False, 
        label='Año',
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_nombre()
        self.populate_linea()
        self.populate_anio()

    def populate_nombre(self):
        consultores = Consultores.objects.values_list('Documento', 'Nombre').distinct()
        self.fields['Nombre'].choices = [('', 'Seleccione el Consultor')] + list(consultores)
        
    def populate_linea(self):
        # Si ModuloId necesita opciones dinámicas, añade lógica aquí.
        linea = Linea.objects.values_list('LineaId', 'Linea').distinct()  # Ajusta según tus modelos
        self.fields['LineaId'].choices = [('', 'Seleccione la linea')] + list(linea)

    def populate_anio(self):
        anios = Tarifa_Consultores.objects.values_list('anio', flat=True).distinct()
        self.fields['anio'].choices = [(anio, anio) for anio in anios]


class ClienteFilterForm(forms.Form):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.populate_choices()

    def populate_choices(self):
        self.fields['Nombre_Cliente'].queryset = Clientes.objects.all()
