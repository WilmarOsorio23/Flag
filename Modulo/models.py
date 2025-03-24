from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import re

# Modelos base
class Modulo(models.Model):
    ModuloId = models.AutoField(primary_key=True)
    Modulo = models.TextField(verbose_name="Descripcion", null=True)

    def __str__(self):
        return f"{self.Modulo}"

    class Meta:
        db_table = 'Modulo'


class IPC(models.Model):
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Indice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Indice: {self.Indice}"

    class Meta:
        db_table = 'IPC'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes'], name='primary_key_IPC')
        ]


class IND(models.Model):
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Indice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Indice: {self.Indice}"

    class Meta:
        db_table = 'IND'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes'], name='primary_key_IND')
        ]


class Linea(models.Model):
    LineaId = models.AutoField(primary_key=True)
    Linea = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.LineaId} {self.Linea} "

    class Meta:
        db_table = 'Linea'


class Perfil(models.Model):
    PerfilId = models.AutoField(primary_key=True)
    Perfil = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.PerfilId} {self.Perfil}"

    class Meta:
        db_table = 'Perfil'


class TipoDocumento(models.Model):
    TipoDocumentoID = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=100)
    descripcion=models.CharField(max_length=50)

    def __str__(self):
        return f"{self.Nombre} {self.TipoDocumentoID} {self.descripcion}"

    class Meta:
        db_table = 'TipoDocumento'

class Cargos(models.Model):
    CargoId = models.AutoField(primary_key=True)
    Cargo = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Cargo}"

    class Meta:
        db_table = 'Cargos'

# Modelos con relaciones
class Clientes(models.Model):
    ClienteId = models.AutoField(primary_key=True)
    TipoDocumentoID = models.ForeignKey(
        TipoDocumento, 
        on_delete=models.CASCADE,
        db_column='TipoDocumentoID'
    )   
    DocumentoId = models.CharField(max_length=20)
    Nombre_Cliente = models.CharField(max_length=50)
    Activo = models.BooleanField(default=True)
    Fecha_Inicio = models.DateField()
    Fecha_Retiro = models.DateField(null=True, blank=True)
    Direccion = models.CharField(max_length=100, null=True, blank=True)
    Telefono = models.CharField(max_length=20, null=True, blank=True)
    CorreoElectronico = models.CharField(max_length=100, null=True, blank=True)
    ContactoID = models.ForeignKey(
        'Contactos', 
        on_delete=models.CASCADE,
        db_column='ContactoID',
        null=True,  # Permitir valores nulos
        blank=True  # Hacerlo opcional
    )
    BuzonFacturacion = models.CharField(max_length=100, null=True, blank=True)
    TipoCliente = models.CharField(max_length=20, null=True, blank=True)
    Ciudad = models.CharField(max_length=50, null=True, blank=True)
    Departamento = models.CharField(max_length=20, null=True, blank=True)
    Pais = models.CharField(max_length=20, null=True, blank=True)
    Nacional = models.BooleanField(default=False)

    def clean(self):
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
        super().clean()
        #CorreoElectronico: Validar que sea un correo electrónico válido, en formato.
        if self.CorreoElectronico:
            email_validator = EmailValidator()
            try:
                email_validator(self.CorreoElectronico)
            except ValidationError:
                raise ValidationError({'CorreoElectronico': 'El correo electrónico no es válido.'})
        
        #Telefono: Validar que contenga solo números y opcionalmente algunos caracteres especiales como +, -, (), y espacios.
        if self.Telefono:
            if not re.match(r'^[\d\+\-\(\) ]+$', self.Telefono):
                raise ValidationError({'Telefono': 'El teléfono contiene caracteres no permitidos.'})
        
        # Validar BuzonFacturacion (si se espera que sea un correo electrónico)
        if self.BuzonFacturacion:
            email_validator = EmailValidator()
            try:
                email_validator(self.BuzonFacturacion)
            except ValidationError:
                raise ValidationError({'BuzonFacturacion': 'El buzón de facturación no es válido.'})
        
        #Ciudad, Departamento y Pais: Validar que no contengan caracteres especiales no permitidos.
         # Validar Ciudad, Departamento, Pais
        if self.Ciudad:
            if not re.match(r'^[\w\s\-]+$', self.Ciudad):
                raise ValidationError({'Ciudad': 'La ciudad contiene caracteres no permitidos.'})
        
        if self.Departamento:
            if not re.match(r'^[\w\s\-]+$', self.Departamento):
                raise ValidationError({'Departamento': 'El departamento contiene caracteres no permitidos.'})
        
        if self.Pais:
            if not re.match(r'^[\w\s\-]+$', self.Pais):
                raise ValidationError({'Pais': 'El país contiene caracteres no permitidos.'})


    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Clientes.
        """
        tipo_documento_nombre = self.TipoDocumentoID.Nombre if self.TipoDocumentoID else "Sin TipoDocumento"
        tipo_documento_id = self.TipoDocumentoID.TipoDocumentoID if self.TipoDocumentoID else "Sin ID"
        contacto_nombre = self.ContactoID.Nombre if self.ContactoID else "Sin Contacto"
        contacto_id = self.ContactoID.id if self.ContactoID else "Sin ID"
        return f'{tipo_documento_nombre} - {tipo_documento_id} - {self.DocumentoId} - {self.Nombre_Cliente} - {contacto_nombre} - {contacto_id}'

    class Meta:
        db_table = 'Clientes'
        constraints = [
            models.UniqueConstraint(fields=['TipoDocumentoID', 'DocumentoId'], name='unique_cliente'),
        ]

class Tiempos_Cliente(models.Model):
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Documento = models.CharField(max_length=20)
    ClienteId = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')
    LineaId = models.ForeignKey('Linea', on_delete=models.CASCADE, db_column='LineaId')
    Horas = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Documento: {self.Documento}, Cliente: {self.ClienteId}, Horas: {self.Horas}"

    class Meta:
        db_table = 'Tiempos_Cliente'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'Documento', 'ClienteId', 'LineaId'], name='unique_tiempos_cliente')
        ]

class Consultores(models.Model):
    Documento = models.CharField(max_length=20, primary_key=True)
    TipoDocumentoID = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, db_column='TipoDocumentoID')
    Nombre = models.CharField(max_length=100)
    Empresa = models.CharField(max_length=100)
    Profesion = models.CharField(max_length=100)
    LineaId = models.ForeignKey(Linea, on_delete=models.CASCADE, db_column='LineaId')
    ModuloId = models.ForeignKey(Modulo, on_delete=models.CASCADE, db_column='ModuloId')
    PerfilId = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column='PerfilId')
    Estado = models.BooleanField(default=True)
    Fecha_Ingreso = models.DateField()
    Fecha_Retiro = models.DateField(null=True, blank=True)
    Direccion = models.CharField(max_length=255, null=True, blank=True, verbose_name="Dirección")
    Telefono = models.CharField(max_length=20, null=True, blank=True, verbose_name="Teléfono")
    Fecha_Operacion = models.DateField(null=True, blank=True)
    Certificado = models.BooleanField(default=True)
    Certificaciones = models.CharField(max_length=255, null=True, blank=True)  # Ensure this field is properly defined
    Fecha_Nacimiento = models.DateField(null=True, blank=True)
    Anio_Evaluacion = models.CharField(max_length=4, null=True, blank=True)
    NotaEvaluacion = models.DecimalField(max_digits=4, decimal_places=2,null=True, blank=True)

    def clean(self):
        # Verificar que Fecha_Ingreso no sea anterior a Fecha_Nacimiento si ambas fechas están presentes
        if self.Fecha_Nacimiento and self.Fecha_Ingreso and self.Fecha_Ingreso < self.Fecha_Nacimiento:
            raise ValidationError('La fecha de ingreso no puede ser anterior a la fecha de nacimiento.')

    def __str__(self):
        return f'{self.TipoDocumentoID} - {self.Documento} - {self.Nombre} - {self.Certificado} - {self.Certificaciones}'

    class Meta:
        db_table = 'Consultores'

class Certificacion(models.Model):
    CertificacionId = models.AutoField(primary_key=True)
    Certificacion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Certificacion}"

    class Meta:
        db_table = 'Certificacion'

class Detalle_Certificacion(models.Model):
    Id = models.AutoField(primary_key=True)
    Documento= models.ForeignKey('Empleado', on_delete=models.CASCADE, db_column='Documento')
    CertificacionId= models.ForeignKey(Certificacion, on_delete=models.CASCADE, db_column='CertificacionId')
    Fecha_Certificacion=models.DateField()

    def __str__(self):
        return f"Id: {self.Id}, Documento: {self.Documento}, CertificaciónId: {self.CertificacionId}, Fecha_Certificacion: {self.Fecha_Certificacion}"

    class Meta:
        db_table = 'Detalle_Certificacion'
     

class Concepto(models.Model):
    ConceptoId = models.AutoField(primary_key=True)
    Descripcion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Descripcion}"

    class Meta:
        db_table = 'Concepto'

class TiemposConcepto(models.Model):
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Documento = models.CharField(max_length=20)
    ConceptoId = models.ForeignKey('Concepto', on_delete=models.CASCADE, db_column='ConceptoId')
    LineaId = models.ForeignKey('Linea', on_delete=models.CASCADE, db_column='LineaId')
    Horas = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Documento: {self.Documento}, Concepto: {self.ConceptoId}, Horas: {self.Horas}"

    class Meta:
        db_table = 'Tiempos_Concepto'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'Documento', 'ConceptoId', 'LineaId'], name='unique_tiempos_concepto')
        ]
class Gastos(models.Model):
    GastoId = models.AutoField(primary_key=True)
    Gasto = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Gasto}"

    class Meta:
        db_table = 'Gastos'

class Detalle_Gastos(models.Model):
    id = models.AutoField(primary_key=True)
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    GastosId = models.ForeignKey(Gastos, on_delete=models.CASCADE, db_column='GastosId')
    Valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Id:{self.id}, Año: {self.Anio}, Mes: {self.Mes}, Gasto ID: {self.GastosId}, Valor: {self.Valor}"

    class Meta:
        db_table = 'Detalle_Gastos'
        

class Total_Gastos(models.Model):
    id = models.AutoField(primary_key=True)
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Total = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"id:{self.id}, Año: {self.Anio}, Mes: {self.Mes}, Total: {self.Total}"

    class Meta:
        db_table = 'Total_Gastos'
        

class Costos_Indirectos(models.Model):
    CostoId = models.AutoField(primary_key=True)
    Costo = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Costo}"

    class Meta:
        db_table = 'Costos_Indirectos'

class Detalle_Costos_Indirectos(models.Model):
    Id = models.AutoField(primary_key=True)
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    CostosId = models.ForeignKey(Costos_Indirectos, on_delete=models.CASCADE, db_column='CostosId')
    Valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"id: {self.Id}, Año:{self.Anio}, Mes: {self.Mes}, Costo ID: {self.CostosId}, Valor: {self.Valor}"

    class Meta:
        db_table = 'Detalle_Costos_Indirectos'

class Total_Costos_Indirectos(models.Model):
    id = models.AutoField(primary_key=True)
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Total = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Total: {self.Total}"

    class Meta:
        db_table = 'Total_Costos_Indirectos'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes'], name='unique_total_costos_indirectos')
        ]

class Nomina(models.Model):
    NominaId = models.AutoField(primary_key=True)
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Documento = models.ForeignKey('Empleado', on_delete=models.CASCADE, db_column='Documento')
    Salario = models.DecimalField(max_digits=10, decimal_places=2)
    Cliente = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')

    def __str__(self):
        return f'NominaId:{self.NominaId} Año: {self.Anio}, Mes: {self.Mes}, Documento: {self.Documento}, Salario: {self.Salario}, Cliente: {self.Cliente}'

    class Meta:
        db_table = 'Nomina'
        
class Empleado(models.Model):
    Documento = models.CharField(max_length=20, primary_key=True)
    TipoDocumento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, db_column='TipoDocumento')
    Nombre = models.CharField(max_length=100)
    FechaNacimiento = models.DateField()
    FechaIngreso = models.DateField()
    FechaOperacion = models.DateField()
    ModuloId = models.ForeignKey(Modulo, on_delete=models.CASCADE, db_column='ModuloId')
    PerfilId = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column='PerfilId')
    LineaId = models.ForeignKey(Linea, on_delete=models.CASCADE, db_column='LineaId')
    CargoId = models.ForeignKey(Cargos, on_delete=models.CASCADE, db_column='CargoId')  # Cambiado aquí
    Activo =  models.BooleanField(default=True)
    TituloProfesional = models.CharField(max_length=100)
    FechaGrado = models.DateField()
    Universidad = models.CharField(max_length=100)
    ProfesionRealizada = models.CharField(max_length=100)
    AcademiaSAP = models.BooleanField(max_length=100)
    CertificadoSAP = models.BooleanField(default=True)  # tinyint(1) => BooleanField
    OtrasCertificaciones = models.BooleanField(max_length=100)  # Cambiado a CharField
    Postgrados = models.BooleanField(max_length=100)  # Cambiado a CharField
    Activo = models.BooleanField(default=True)
    FechaRetiro = models.DateField(null=True, blank=True)
    Direccion = models.CharField(max_length=255, null=True, blank=True)
    Ciudad = models.CharField(max_length=100, null=True, blank=True)
    Departamento = models.CharField(max_length=100, null=True, blank=True)
    DireccionAlterna = models.CharField(max_length=255, null=True, blank=True)
    Telefono1 = models.CharField(max_length=20, null=True, blank=True)
    Telefono2 = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'Empleado'

    def __str__(self):
        return f"{self.Nombre} - {self.TipoDocumento} {self.Documento}"
    
     
    def clean(self):
        if self.FechaIngreso < self.FechaNacimiento:
            raise ValidationError('La fecha de ingreso no puede ser anterior a la fecha de nacimiento.')


class TiposContactos(models.Model):
    contactoId= models.AutoField(primary_key=True)
    Descripcion= models.CharField(max_length=50)

    def __str__(self):
        return f"id:{self.contactoId}, descripcion:{self.Descripcion}"

    class Meta:
        db_table = 'Tipos_Contactos'

class Contactos(models.Model):
    id = models.AutoField(primary_key=True)
    clienteId = models.ForeignKey(Clientes, on_delete=models.CASCADE, db_column='ClienteId')
    contactoId = models.ForeignKey(TiposContactos, on_delete=models.CASCADE, db_column='contactoId')
    Nombre = models.CharField(max_length=100)
    Telefono = models.CharField(max_length=20, null=True, blank=True)
    Direccion = models.CharField(max_length=255, null=True, blank=True)
    Cargo = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        #return f"id: {self.id}, ClienteId: {self.clienteId}, ContactoId: {self.contactoId}, Nombre: {self.Nombre}, Telefono: {self.Telefono}, Direccion: {self.Direccion}, CargoId: {self.Cargo}, Activo: {self.activo}"
        return f"id: {self.id}, Nombre: {self.Nombre}"
    class Meta:
        db_table = 'Contactos'

class Historial_Cargos(models.Model):
    id = models.AutoField(primary_key=True)
    documentoId=models.ForeignKey('Empleado', on_delete=models.CASCADE, db_column='documentoId')
    cargoId = models.ForeignKey('Cargos', on_delete=models.CASCADE, db_column='CargoId')
    FechaInicio = models.DateField()
    FechaFin = models.DateField(null=True)

    def __str__(self):
        return f"id: {self.id}, DocumentoId: {self.documentoId}, CargoId: {self.cargoId}, FechaInicio: {self.FechaInicio}, FechaFin: {self.FechaFin}"

    class Meta:
        db_table = 'Historial_Cargos'

class Empleados_Estudios(models.Model):
    id = models.AutoField(primary_key=True)
    documentoId = models.ForeignKey('Empleado', on_delete=models.CASCADE, db_column='documentoId')
    titulo = models.CharField(max_length=100)
    institucion = models.CharField(max_length=100)
    fecha_Inicio = models.DateField()
    fecha_Fin = models.DateField()
    fecha_Graduacion = models.DateField()

    def __str__(self):
        return f"id: {self.id}, DocumentoId: {self.documentoId}, Titulo: {self.titulo}, Institucion: {self.institucion}, FechaInicio: {self.fecha_Inicio}, FechaFin: {self.fecha_Fin}, FechaGraduacion: {self.fecha_Graduacion}"

    class Meta:
        db_table = 'Empleados_Estudios'

class Horas_Habiles(models.Model):
    id = models.AutoField(primary_key=True)
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Dias_Habiles = models.IntegerField()
    Horas_Laborales = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Días Hábiles: {self.Dias_Habiles}, Horas Laborales: {self.Horas_Laborales}"

    class Meta:
        db_table = 'Horas_Habiles'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes'], name='unique_horas_habiles')
        ]


class Tarifa_Consultores(models.Model):
    id = models.AutoField(primary_key=True)
    documentoId = models.ForeignKey('Consultores', on_delete=models.CASCADE, db_column='documentoId')
    anio = models.CharField(max_length=4, db_column='anio')
    mes = models.CharField(max_length=2, db_column='mes')
    clienteID = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='clienteID')
    valorHora = models.DecimalField(max_digits=10, decimal_places=2, db_column='valorHora')
    valorDia = models.DecimalField(max_digits=10, decimal_places=2, db_column='valorDia')
    valorMes = models.DecimalField(max_digits=10, decimal_places=2, db_column='valorMes')
    monedaId = models.ForeignKey('moneda', on_delete=models.CASCADE, db_column='monedaId')

    def __str__(self):
        return f"id: {self.id}, DocumentoId: {self.documentoId}, Año: {self.anio}, Mes: {self.mes}, ClienteId: {self.clienteID}, ValorHora: {self.valorHora}, ValorDia: {self.valorDia}, ValorMes: {self.valorMes}, Moneda: {self.id}"

    class Meta:
        db_table = 'Tarifa_Consultores'

class Moneda(models.Model):
    id = models.AutoField(primary_key=True) 
    Nombre= models.CharField(max_length=10)
    descripcion = models.CharField(max_length=20)

    def __str__(self):
        return f"id:{self.id}, Nombre:{self.Nombre} descripcion:{self.descripcion}"

    class Meta:
        db_table = 'moneda'


class TiemposFacturables(models.Model):
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    LineaId = models.ForeignKey('Linea', on_delete=models.CASCADE, db_column='LineaId')
    ClienteId = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')
    Horas = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Linea: {self.LineaId}, Cliente: {self.ClienteId}, Horas: {self.Horas}"

    class Meta:
        db_table = 'Tiempos_Facturables'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'LineaId', 'ClienteId'], name='unique_tiempos_facturables')
        ]


class ClientesContratos(models.Model):
    ClientesContratosId = models.AutoField(primary_key=True)
    ClienteId = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')
    FechaInicio = models.DateField(null=False, blank=False)
    FechaFin = models.DateField(null=True, blank=True)
    Contrato = models.CharField(max_length=50,null=True,blank=True)  # Cambiado a CharField
    ContratoVigente = models.BooleanField(default=True)
    OC_Facturar =  models.BooleanField(default=True)
    Parafiscales =  models.BooleanField(default=True)
    HorarioServicio = models.TextField(null=True, blank=True)
    FechaFacturacion = models.TextField(null=True, blank=True)
    TipoFacturacion = models.TextField(null=True, blank=True)
    Observaciones = models.TextField(null=True, blank=True)
    Polizas = models.BooleanField(default=False)
    PolizasDesc = models.CharField(max_length=200,null=True,blank=True)
    #ContratoValor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    IncluyeIvaValor = models.BooleanField(default=False)
    ContratoDesc = models.CharField(max_length=200,null=True,blank=True)
    ServicioRemoto = models.BooleanField(default=False)

    class Meta:
        db_table = 'Clientes_Contratos'

    def __str__(self):
        return f"ContratoId:{self.ClientesContratosId} - Cliente: {self.ClienteId} - FechaInicio: {self.FechaInicio} - FechaFin: {self.FechaFin} - Contrato: {self.Contrato} - ContratoVigente: {self.ContratoVigente} - OC_Facturar: {self.OC_Facturar} - Parafiscales: {self.Parafiscales} - HorarioServicio: {self.HorarioServicio} - FechaFacturacion: {self.FechaFacturacion} - TipoFacturacion: {self.TipoFacturacion} - Observaciones: {self.Observaciones} - Polizas: {self.Polizas} - PolizasDesc: {self.PolizasDesc} - IncluyeIvaValor: {self.IncluyeIvaValor} - ContratoDesc: {self.ContratoDesc} - ServicioRemoto: {self.ServicioRemoto}"
    
    
class Tarifa_Clientes(models.Model):
    id = models.AutoField(primary_key=True)
    clienteId = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='clienteId')
    lineaId = models.ForeignKey('Linea', on_delete=models.CASCADE, db_column='lineaId')
    moduloId = models.ForeignKey('Modulo', on_delete=models.CASCADE, db_column='moduloId')  
    anio = models.IntegerField()
    mes = models.IntegerField()
    valorHora = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valorDia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valorMes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bolsaMes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valorBolsa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monedaId = models.ForeignKey('Moneda', on_delete=models.CASCADE, db_column='monedaId')
    referenciaId= models.ForeignKey('Referencia', on_delete=models.CASCADE, db_column='referenciaId')
    centrocostosId = models.ForeignKey('CentrosCostos', on_delete=models.CASCADE, db_column='centrocostosId')
    iva = models.FloatField(null=True, blank=True)
    sitioTrabajo = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"id: {self.id}, ClienteId: {self.clienteId}, LineaId: {self.lineaId}, ModuloId: {self.moduloId}, Anio: {self.anio}, Mes: {self.mes}, ValorHora: {self.valorHora}, ValorDia: {self.valorDia}, ValorMes: {self.valorMes}, BolsaMes: {self.bolsaMes}, MonedaId: {self.monedaId}, ReferenciaId: {self.referenciaId}, CentroCostosId: {self.centrocostosId}, IVA: {self.iva}, SitioTrabajo: {self.sitioTrabajo}"

    class Meta:
        db_table = 'Tarifa_Clientes'

class FacturacionClientes(models.Model):
    ConsecutivoId = models.AutoField(primary_key=True)
    Anio = models.IntegerField()
    Mes = models.IntegerField(null=True, blank=True)
    ClienteId = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')
    LineaId = models.ForeignKey('Linea', on_delete=models.CASCADE, db_column='LineaId')
    ModuloId = models.ForeignKey('Modulo', on_delete=models.CASCADE, db_column='ModuloId')
    Factura = models.TextField(null=True, blank=True)
    HorasFactura = models.FloatField(null=True, blank=True)
    Valor_Horas = models.FloatField(null=True, blank=True)
    DiasFactura = models.FloatField(null=True, blank=True)
    Valor_Dias = models.FloatField(null=True, blank=True)
    MesFactura = models.IntegerField(null=True, blank=True)
    Valor_Meses = models.FloatField(null=True, blank=True)
    Bolsa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    Valor_Bolsa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    Valor = models.FloatField(null=True, blank=True)
    Descripcion = models.TextField(null=True, blank=True)
    IVA = models.FloatField(null=True, blank=True)
    Referencia= models.TextField(null=True, blank=True)
    Ceco = models.TextField(null=True, blank=True)
    Sitio_Serv = models.TextField(null=True, blank=True)


    class Meta:
        db_table = 'Facturacion_Clientes'

    def __str__(self):
        return f"Facturación {self.ConsecutivoId} - Cliente {self.ClienteId} - Linea {self.LineaId}"
    
class Referencia(models.Model):
    id = models.AutoField(primary_key=True)
    codigoReferencia = models.CharField(max_length=20)
    descripcionReferencia = models.CharField(max_length=60)

    def __str__(self):
        return f"id: {self.id}, codigoReferencia: {self.codigoReferencia}, Referencia: {self.descripcionReferencia}"

    class Meta:
        db_table = 'Referencias'


class CentrosCostos(models.Model):
    id= models.AutoField(primary_key=True)
    codigoCeCo= models.CharField(max_length=20)
    descripcionCeCo= models.CharField(max_length=60)

    def __str__(self):
        return f"{self.id} - {self.codigoCeCo} - {self.descripcionCeCo}"

    class Meta:
        db_table = 'Centros_Costos'
    

class Ind_Operat_Clientes(models.Model):
    Id = models.AutoField(primary_key=True)
    Anio = models.IntegerField()
    Mes = models.IntegerField()
    LineaId = models.ForeignKey('Linea', on_delete=models.CASCADE, db_column='LineaId')
    HorasTrabajadas = models.FloatField()
    HorasFacturables = models.FloatField()

    class Meta:
        db_table = 'Ind_Operat_Clientes'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'LineaId'], name='unique_Ind_Operat_Clientes')
        ]

    def __str__(self):
        return f"ID {self.id} - Año {self.Anio} - Mes {self.Mes} - Linea {self.Linea_id}"
    
class Ind_Operat_Conceptos(models.Model):
    Id = models.AutoField(primary_key=True)
    Anio = models.IntegerField()
    Mes = models.IntegerField()
    LineaId = models.ForeignKey('Linea', on_delete=models.CASCADE, db_column='LineaId')
    ConceptoId = models.ForeignKey('Concepto', on_delete=models.CASCADE, db_column='ConceptoId')
    HorasConcepto = models.FloatField()

    class Meta:
        db_table = 'Ind_Operat_Conceptos'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'LineaId', 'ConceptoId'], name='unique_Ind_Operat_Conceptos')
        ]

    def __str__(self):
        return f"ID {self.Id} - Año {self.Anio} - Mes {self.Mes} - Linea {self.LineaId} - Concepto {self.ConceptoId}"
    
class ContratosOtrosSi(models.Model):
    ContratosOtrosSiId = models.AutoField(primary_key=True)
    ClienteId = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')
    FechaInicio = models.DateField(null=False, blank=False)
    FechaFin = models.DateField(null=True, blank=True)
    NumeroOtroSi = models.CharField(max_length=20,null=True,blank=True) 
    ValorOtroSi = models.DecimalField(max_digits=10, decimal_places=2)
    ValorIncluyeIva = models.BooleanField(default = 0)
    Polizas = models.BooleanField(default=0)
    PolizasDesc = models.CharField(max_length=200,null=True,blank=True)
    FirmadoFlag = models.BooleanField(default=0)
    FirmadoCliente = models.BooleanField(default=0)


    class Meta:
        db_table = 'Contratos_OtrosSi'

    def __str__(self):
        return f"ContratoId:{self.ContratosOtrosSiId} - Cliente: {self.ClienteId} - FechaInicio: {self.FechaInicio} - FechaFin: {self.FechaFin} - NumeroOtroSi: {self.NumeroOtroSi} - ValorOtroSi: {self.ValorOtroSi} - ValorIncluyeIva: {self.ValorIncluyeIva} - Polizas: {self.Polizas} - PolizasDesc: {self.PolizasDesc} - FirmadoFlag: {self.FirmadoFlag} - FirmadoCliente: {self.FirmadoCliente}"