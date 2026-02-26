# Add centrocostosId to TiemposConcepto for CeCo per tiempo concepto

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modulo', '0008_empleados_estudios_fechas_opcionales'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiemposconcepto',
            name='centrocostosId',
            field=models.ForeignKey(
                blank=True,
                db_column='centrocostosId',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='modulo.centroscostos',
            ),
        ),
    ]
