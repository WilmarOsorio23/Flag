from django.db import models

class Modulo(models.Model):
    id = models.AutoField(primary_key=True)
    Nombre = models.TextField(verbose_name="Descripcion", null=True)

    def __str__(self):
        fila = "Nombre" + self.Nombre
        return fila

    def delete(self, using=None, Keep_parents=False):
        super().delete()