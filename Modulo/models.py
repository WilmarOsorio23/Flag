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

