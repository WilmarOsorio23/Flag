from django.db import models
from django.forms import ValidationError

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

    def __str__(self):
        return f"{self.Nombre} {self.TipoDocumentoID}"

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

    def __str__(self):
        return f'{self.TipoDocumentoID.Nombre} - {self.TipoDocumentoID.TipoDocumentoID} - {self.DocumentoId} - {self.Nombre_Cliente}'

    class Meta:
        db_table = 'Clientes'
        constraints = [
            models.UniqueConstraint(fields=['TipoDocumentoID', 'DocumentoId'], name='unique_cliente')
        ]

class Tiempos_Cliente(models.Model):
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Documento = models.CharField(max_length=20)
    ClienteId = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')
    Horas = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Documento: {self.Documento}, Cliente: {self.ClienteId}, Horas: {self.Horas}"

    class Meta:
        db_table = 'Tiempos_Cliente'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'Documento', 'ClienteId'], name='unique_tiempos_cliente')
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
    Fecha_Operacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.TipoDocumentoID} - {self.Documento} - {self.Nombre}' 

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
    Horas = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Documento: {self.Documento}, Concepto: {self.ConceptoId}, Horas: {self.Horas}"

    class Meta:
        db_table = 'Tiempos_Concepto'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'Documento', 'ConceptoId'], name='unique_tiempos_concepto')
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

class Cargos(models.Model):
    CargoId = models.AutoField(primary_key=True)
    Cargo = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Cargo}"

    class Meta:
        db_table = 'Cargos'
        
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
    TituloProfesional = models.CharField(max_length=100)
    FechaGrado = models.DateField()
    Universidad = models.CharField(max_length=100)
    ProfesionRealizada = models.CharField(max_length=100)
    TituloProfesionalActual = models.CharField(max_length=100)
    UniversidadActual = models.CharField(max_length=100)
    AcademiaSAP = models.CharField(max_length=100)
    CertificadoSAP = models.BooleanField()  # tinyint(1) => BooleanField
    OtrasCertificaciones = models.CharField(max_length=100)  # Cambiado a CharField
    Postgrados = models.CharField(max_length=100)  # Cambiado a CharField

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
    id=models.AutoField(primary_key=True),
    clienteId = models.ForeignKey(Clientes, on_delete=models.CASCADE, db_column='ClienteId')
    contactoId = models.ForeignKey(TiposContactos, on_delete=models.CASCADE, db_column='contactoId')
    Nombre = models.CharField(max_length=100)
    Telefono = models.CharField(max_length=20, null=True, blank=True)
    Direccion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"id: {self.id}, ClientedId: {self.clienteId}, ContactoId: {self.contactoId}, Nombre: {self.Nombre}, telefono: {self.Telefono}, Direccion: {self.Direccion}"

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