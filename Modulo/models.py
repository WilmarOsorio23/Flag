from django.db import models

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
        return f"{self.Linea}"

    class Meta:
        db_table = 'Linea'


class Perfil(models.Model):
    PerfilId = models.AutoField(primary_key=True)
    Perfil = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.Perfil}"

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
    Colaborador = models.CharField(max_length=100)
    ClienteId = models.ForeignKey(Clientes, on_delete=models.CASCADE, db_column='ClienteId')
    Horas = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Colaborador: {self.Colaborador}, Cliente: {self.ClienteId}, Horas: {self.Horas}"

    class Meta:
        db_table = 'Tiempos_Cliente'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'Colaborador', 'ClienteId'], name='unique_tiempos_cliente')
        ]

class Consultores(models.Model):
    TipoDocumentoID = models.ForeignKey(
        TipoDocumento, 
        on_delete=models.CASCADE,
        db_column='TipoDocumentoID'
    )
    Documento = models.CharField(max_length=20)
    Nombre = models.CharField(max_length=100)
    Empresa = models.CharField(max_length=100)
    Profesion = models.CharField(max_length=100)
    LineaId = models.ForeignKey(
        Linea, 
        on_delete=models.CASCADE,
        db_column='LineaId'
    )
    ModuloId = models.ForeignKey(
        Modulo, 
        on_delete=models.CASCADE,
        db_column='ModuloId'
    )
    PerfilId = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        db_column='PerfilId'
    )
    Estado = models.BooleanField(default=True)
    Fecha_Ingreso = models.DateField()
    Fecha_Retiro = models.DateField(null=True, blank=True)
    Direccion = models.CharField(max_length=255, null=True, blank=True)
    Telefono = models.CharField(max_length=20, null=True, blank=True)
    Fecha_Operacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.TipoDocumentoID} - {self.Documento} - {self.Nombre}'

    class Meta:
        db_table = 'Consultores'
        constraints = [
            models.UniqueConstraint(fields=['TipoDocumentoID', 'Documento'], name='unique_consultor')
        ]

class Certificacion(models.Model):
    CertificacionId = models.AutoField(primary_key=True)
    Certificacion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Certificacion}"

    class Meta:
        db_table = 'Certificacion'

class Detalle_Certificacion(models.Model):
    DocumentoId = models.CharField(max_length=50)
    CertificacionId = models.ForeignKey(Certificacion, on_delete=models.CASCADE, db_column='CertificacionId')
    Fecha_Certificacion = models.DateField()

    def __str__(self):
        return f"Documento ID: {self.DocumentoId}, Certificación ID: {self.CertificacionId}, Fecha: {self.Fecha_Certificacion}"

    class Meta:
        db_table = 'Detalle_Certificacion'
        constraints = [
            models.UniqueConstraint(fields=['DocumentoId', 'CertificacionId'], name='unique_detalle_certificacion')
        ]

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
    Colaborador = models.CharField(max_length=100)
    ConceptoId = models.ForeignKey(Concepto, on_delete=models.CASCADE, db_column='ConceptoId')
    Horas = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Colaborador: {self.Colaborador}, Concepto: {self.ConceptoId}, Horas: {self.Horas}"

    class Meta:
        db_table = 'Tiempos_Concepto'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'Colaborador', 'ConceptoId'], name='unique_tiempos_concepto')
        ]


class Gastos(models.Model):
    GastoId = models.AutoField(primary_key=True)
    Gasto = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Gasto}"

    class Meta:
        db_table = 'Gastos'


class Detalle_Gastos(models.Model):
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    GastosId = models.ForeignKey(Gastos, on_delete=models.CASCADE, db_column='GastosId')
    Valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Gasto ID: {self.GastosId}, Valor: {self.Valor}"

    class Meta:
        db_table = 'Detalle_Gastos'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'GastosId'], name='unique_detalle_gastos')
        ]


class Total_Gastos(models.Model):
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Total = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Total: {self.Total}"

    class Meta:
        db_table = 'Total_Gastos'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes'], name='unique_total_gastos')
        ]

class Costos_Indirectos(models.Model):
    CostoId = models.AutoField(primary_key=True)
    Costo = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Costo}"

    class Meta:
        db_table = 'Costos_Indirectos'

class Detalle_Costos_Indirectos(models.Model):
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    CostosId = models.ForeignKey(Costos_Indirectos, on_delete=models.CASCADE, db_column='CostosId')
    Valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Costos ID: {self.CostosId}, Valor: {self.Valor}"

    class Meta:
        db_table = 'Detalle_Costos_Indirectos'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'CostosId'], name='unique_detalle_costos_indirectos')
        ]

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
    Documento = models.CharField(max_length=10)
    Salario = models.DecimalField(max_digits=10, decimal_places=2)
    Cliente = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')

    def __str__(self):
        return f'Año: {self.Anio}, Mes: {self.Mes}, Documento: {self.Documento}, Salario: {self.Salario}'

    class Meta:
        db_table = 'Nomina'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes', 'Documento'], name='unique_nomina')
        ]

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
    CertificadoSAP = models.CharField(max_length=100)
    OtrasCertificaciones = models.TextField()
    Postgrados = models.TextField()

    class Meta:
        db_table = 'Empleado'
        unique_together = (('TipoDocumento', 'Documento'),)

    def __str__(self):
        return f"{self.Nombre} - {self.TipoDocumento} {self.Documento}"


