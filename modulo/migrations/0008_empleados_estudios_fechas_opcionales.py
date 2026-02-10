# Generated manually - Fecha Inicio y Fecha Fin opcionales en Empleados_Estudios

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulo', '0007_cargos_remove_empleado_cargo_empleado_cargoid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empleados_estudios',
            name='fecha_Inicio',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='empleados_estudios',
            name='fecha_Fin',
            field=models.DateField(blank=True, null=True),
        ),
    ]
