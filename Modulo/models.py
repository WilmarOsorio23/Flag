from django.db import models

class Modulo(models.Model):
    id = models.AutoField(primary_key=True)
    Nombre = models.TextField(verbose_name="Descripcion", null=True)

    def __str__(self):
        fila = "Nombre" + self.Nombre
        return fila

    def delete(self, using=None, Keep_parents=False):
        super().delete()

    class Meta:
        db_table = 'Modulo'

class IPC(models.Model):
    anio = models.CharField(max_length=4)
    mes = models.CharField(max_length=2)
    campo_numerico = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Año: {self.anio}, Mes: {self.mes}, Campo Numérico: {self.campo_numerico}"

    def delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        db_table = 'IPC'

class Clientes(models.Model):
    ClienteId = models.AutoField(primary_key=True)
    TipoDocumentoID = models.CharField(max_length=10)
    DocumentoId = models.CharField(max_length=20)
    Nombre_Cliente = models.CharField(max_length=50)
    Activo = models.BooleanField(default=True)
    Fecha_Inicio = models.DateField()
    Fecha_Retiro = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.TipoDocumentoID} - {self.DocumentoId} - {self.Nombre_Cliente}'

    def delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        db_table = 'Clientes'
        constraints = [
            models.UniqueConstraint(fields=['TipoDocumentoID', 'DocumentoId'], name='unique_cliente')
        ]

class Consultores(models.Model):
    TipoDocumentoId = models.CharField(max_length=10)
    Documento = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=100)
    Empresa = models.CharField(max_length=100)
    Profesion = models.CharField(max_length=100)
    LineaId = models.CharField(max_length=50)  # Temporalmente como CharField
    ModuloId = models.CharField(max_length=50)  # Temporalmente como CharField
    Perfil = models.CharField(max_length=50)  # Temporalmente como CharField
    Estado = models.BooleanField(default=True)
    Fecha_Ingreso = models.DateField()
    Fecha_Retiro = models.DateField(null=True, blank=True)
    Direccion = models.CharField(max_length=255, null=True, blank=True)
    Telefono = models.CharField(max_length=20, null=True, blank=True)
    Fecha_Operacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.TipoDocumentoId} - {self.Documento} - {self.Nombre}'

    class Meta:
        db_table = 'Consultores'
        constraints = [
            models.UniqueConstraint(fields=['TipoDocumentoId', 'Documento'], name='unique_consultor')
        ]

