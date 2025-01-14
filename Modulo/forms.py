from django import forms
from .models import Modulo, IPC, IND, Linea, Perfil, TipoDocumento, Clientes, Consultores, Certificacion, Costos_Indirectos
from .models import Concepto, Gastos, Detalle_Gastos, Total_Gastos, Total_Costos_Indirectos
from .models import Detalle_Costos_Indirectos, TiemposConcepto, Tiempos_Cliente, Nomina, Detalle_Certificacion, Empleado
from .models import Cargos
from django import forms
from .models import Modulo
from .models import TiposContactos

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
    class Meta:
        model = Clientes
        fields = '__all__'
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
            'Activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
                }),
            'Fecha_Inicio': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
                }),
            'Fecha_Retiro': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
                }),
        }  
        
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

class ConsultoresForm(forms.ModelForm):
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
            'Fecha_Operacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fecha de Operacion (opcional)',
                'type': 'number'
            }),
        }
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['Fecha_Retiro'].required = False  # Campo no obligatorio
            self.fields['Fecha_Retiro'].label = "Fecha de Retiro (opcional)"    
            self.fields['LineaId'].empty_label = "Selecciona una Línea"
            self.fields['ModuloId'].empty_label = "Selecciona un Módulo"
            self.fields['PerfilId'].empty_label = "Selecciona un Perfil"
            self.fields['Telefono'].required = False  # Permitir campo vacío
            self.fields['Direccion'].required = False  # Permitir campo vacío
            self.fields['Fecha_Retiro'].required = False  # Permitir campo vacío

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
            'nombre': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
        }
        labels = {
            'nombre': 'Nombre',
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
            'GastosId': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el ID del gasto'
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
            'GastosId': 'Gasto ID',
            'Valor': 'Valor',
        }

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
           'CostosId': forms.NumberInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el costo indirecto'
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
            'Costosid':'CostosId',
            'Valor': 'Valor',
        }

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
            'Documento': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el documento'
            }),
            'Salario': forms.NumberInput(attrs={
                'type': 'number',
                'class': 'form-control',
                'placeholder': 'Ingrese el salario'
            }),
            'Cliente': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el cliente'
            }),
        }
        labels = {
            'Anio': 'Año',
            'Mes': 'Mes',
            'Documento': 'Documento',
            'Salario': 'Salario',
            'Cliente': 'Cliente',
        }

class Detalle_CertificacionForm(forms.ModelForm):
    class Meta:
        model = Detalle_Certificacion
        fields = '__all__'
        widgets = {
             'Documento': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'Ingrese el documento'
            }),
            'CertificacionId':forms.NumberInput(attrs={
                'type': 'text',
                'class': 'form-control',
            }),
            'Fecha_Certificacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Seleccione la fecha de nacimiento'}),
        }
        labels = {
            'Documento':'Documento',
            'CertificacionId':'Certificacion id',
            'Fecha_Certificacion':'Fecha de Certificación',
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
            'AcademiaSAP': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la academia SAP'}),
            'CertificadoSAP': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Seleccione una opción'), ('1', 'Sí'), ('0', 'No')]),
            'OtrasCertificaciones': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingrese otras certificaciones', 'rows': 3}),
            'Postgrados': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingrese los postgrados', 'rows': 3}),
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
        }

class EmpleadoFilterForm(forms.Form):
    Nombre = forms.ChoiceField(
        choices=[],  
        required=False, 
        label='Colaborador',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Certificacion = forms.ChoiceField(
        choices=[],  
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

    def __init__(self, *args, **kwargs):
        certificacion_seleccionada = kwargs.pop('certificacion_seleccionada', None)
        super(EmpleadoFilterForm, self).__init__(*args, **kwargs)

        certificaciones = Certificacion.objects.values_list('CertificacionId', 'Certificacion').distinct()
        self.fields['Certificacion'].choices = [('', 'Seleccione la certificación')] + [(certificacion[0], certificacion[1]) for certificacion in certificaciones]

        lineas = Linea.objects.values_list('LineaId', 'Linea').distinct()
        self.fields['LineaId'].choices = [('', 'Seleccione la línea')] + [(linea[0], linea[1]) for linea in lineas]

        empleados = Empleado.objects.values_list('Nombre', flat=True).distinct()
        self.fields['Nombre'].choices = [('', 'Seleccione el colaborador')] + [(empleado, empleado) for empleado in empleados]

        Modulo = Empleado.objects.values_list('ModuloId', flat=True).distinct()
        self.fields['ModuloId'].choices = [('', 'Seleccione el módulo')] + [(modulo, modulo) for modulo in Modulo]

        cargos = Cargos.objects.values_list('CargoId', 'Cargo').distinct()
        self.fields['Cargo'].choices = [('', 'Seleccione el cargo')] + [(cargo[0], cargo[1]) for cargo in cargos]

        self.fields['Anio'].choices = [('', 'Seleccione el año')] + [(str(year), str(year)) for year in range(2022, 2025)]

