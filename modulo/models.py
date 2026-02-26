from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager
import re

class UserRole(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    
    # Permisos de Administración
    can_manage_users = models.BooleanField(default=False)
    can_manage_roles = models.BooleanField(default=False)
    
    # Maestros - Permisos específicos
    can_manage_actividades_pagares = models.BooleanField(default=False)
    can_manage_cargos = models.BooleanField(default=False)
    can_manage_certificacion = models.BooleanField(default=False)
    can_manage_clientes = models.BooleanField(default=False)
    can_manage_conceptos = models.BooleanField(default=False)
    can_manage_consultores = models.BooleanField(default=False)
    can_manage_contactos = models.BooleanField(default=False)
    can_manage_costos_indirectos = models.BooleanField(default=False)
    can_manage_centros_costos = models.BooleanField(default=False)
    can_manage_empleados = models.BooleanField(default=False)
    can_manage_empleados_estudios = models.BooleanField(default=False)
    can_manage_gastos = models.BooleanField(default=False)
    can_manage_horas_habiles = models.BooleanField(default=False)
    can_manage_ind = models.BooleanField(default=False)
    can_manage_ipc = models.BooleanField(default=False)
    can_manage_linea = models.BooleanField(default=False)
    can_manage_linea_cliente_centrocostos = models.BooleanField(default=False)
    can_manage_modulo = models.BooleanField(default=False)
    can_manage_moneda = models.BooleanField(default=False)
    can_manage_perfil = models.BooleanField(default=False)
    can_manage_referencias = models.BooleanField(default=False)
    can_manage_tipo_documento = models.BooleanField(default=False)
    can_manage_tipos_contactos = models.BooleanField(default=False)
    can_manage_tipo_pagare = models.BooleanField(default=False)
    
    # Movimientos - Permisos específicos
    can_manage_clientes_contratos = models.BooleanField(default=False)
    can_manage_contratos_otros_si = models.BooleanField(default=False)
    can_manage_pagare = models.BooleanField(default=False)
    can_manage_detalle_certificacion = models.BooleanField(default=False)
    can_manage_detalle_costos_indirectos = models.BooleanField(default=False)
    can_manage_detalle_gastos = models.BooleanField(default=False)
    can_manage_historial_cargos = models.BooleanField(default=False)
    can_manage_nomina = models.BooleanField(default=False)
    can_manage_registro_tiempos = models.BooleanField(default=False)
    can_manage_tarifa_clientes = models.BooleanField(default=False)
    can_manage_tarifa_consultores = models.BooleanField(default=False)
    can_manage_total_costos_indirectos = models.BooleanField(default=False)
    can_manage_total_gastos = models.BooleanField(default=False)
    can_manage_clientes_factura = models.BooleanField(default=False)
    can_manage_facturacion_consultores = models.BooleanField(default=False)
    
    # Informes - Permisos específicos
    can_view_informe_certificacion = models.BooleanField(default=False)
    can_view_informe_empleado = models.BooleanField(default=False)
    can_view_informe_salarios = models.BooleanField(default=False)
    can_view_informe_estudios = models.BooleanField(default=False)
    can_view_informe_consultores = models.BooleanField(default=False)
    can_view_informe_tarifas_consultores = models.BooleanField(default=False)
    can_view_informe_facturacion = models.BooleanField(default=False)
    can_view_informe_historial_cargos = models.BooleanField(default=False)
    can_view_informe_tarifas_clientes = models.BooleanField(default=False)
    can_view_informe_tiempos_consultores = models.BooleanField(default=False)
    can_view_informe_clientes = models.BooleanField(default=False)
    can_view_informe_clientes_contratos = models.BooleanField(default=False)
    can_view_informe_otros_si = models.BooleanField(default=False)
    can_view_informe_pagares = models.BooleanField(default=False)
    can_view_informe_facturacion_consultores = models.BooleanField(default=False)
    can_view_informe_serv_consultor = models.BooleanField(default=False)
    can_view_informe_facturacion_centrocostos = models.BooleanField(default=False)
    can_view_informe_detalle_facturacion_consultores = models.BooleanField(default=False)
    
    # Indicadores - Permisos específicos
    can_view_indicadores_operatividad = models.BooleanField(default=False)
    can_view_indicadores_totales = models.BooleanField(default=False)
    can_view_indicadores_facturacion = models.BooleanField(default=False)
    can_view_indicadores_margen_cliente = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'user_roles'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Desactivar M2M con grupos y permisos para no requerir tablas intermedias
    groups = None
    user_permissions = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'custom_users'

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
    ModuloId = models.ForeignKey('Modulo', on_delete=models.CASCADE, db_column='ModuloId')

    Horas = models.DecimalField(max_digits=10, decimal_places=2)

    # ✅ En DB es NULLABLE, así debe ser en Django
    centrocostosId = models.ForeignKey(
        'CentrosCostos',
        on_delete=models.SET_NULL,         # ✅ evita borrar tiempos si borran un CECO
        db_column='centrocostosId',
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"Año: {self.Anio}, Mes: {self.Mes}, Documento: {self.Documento}, "
            f"Cliente: {self.ClienteId}, Linea: {self.LineaId}, Modulo: {self.ModuloId}, "
            f"Horas: {self.Horas}, CECO: {self.centrocostosId_id}"
        )

    class Meta:
        db_table = 'Tiempos_Cliente'
        indexes = [
            models.Index(fields=['ClienteId', 'Anio', 'Mes', 'LineaId']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['Anio', 'Mes', 'Documento', 'ClienteId', 'LineaId', 'ModuloId'],
                name='unique_tiempos_cliente'
            )
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
    centrocostosId = models.ForeignKey(
        'CentrosCostos',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='centrocostosId',
    )

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

    def save(self, *args, **kwargs):
        """ Guarda el detalle y actualiza el total del costo indirecto correspondiente. """
        super().save(*args, **kwargs)
        total_gastos = Total_Gastos.objects.filter(Anio=self.Anio, Mes=self.Mes).first()
        if total_gastos:
            total_gastos.actualizar_total()

    def delete(self, *args, **kwargs):
        """ Elimina el detalle y actualiza el total del costo indirecto correspondiente. """
        total_gastos = Total_Gastos.objects.filter(Anio=self.Anio, Mes=self.Mes).first()
        super().delete(*args, **kwargs)
        if total_gastos:
            total_gastos.actualizar_total()

        

class Total_Gastos(models.Model):
    id = models.AutoField(primary_key=True)
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Total: {self.Total}"

    class Meta:
        db_table = 'Total_Gastos'

    def actualizar_total(self):
        """ Calcula la suma de los valores de los detalles asociados según Año y Mes. """
        total = Detalle_Gastos.objects.filter(Anio=self.Anio, Mes=self.Mes).aggregate(
            total=models.Sum('Valor')
        )['total'] or 0
        self.Total = total
        self.save()

        

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
        
    def save(self, *args, **kwargs):
        """ Guarda el detalle y actualiza el total del costo indirecto correspondiente. """
        super().save(*args, **kwargs)
        total_costos = Total_Costos_Indirectos.objects.filter(Anio=self.Anio, Mes=self.Mes).first()
        if total_costos:
            total_costos.actualizar_total()

    def delete(self, *args, **kwargs):
        """ Elimina el detalle y actualiza el total del costo indirecto correspondiente. """
        total_costos = Total_Costos_Indirectos.objects.filter(Anio=self.Anio, Mes=self.Mes).first()
        super().delete(*args, **kwargs)
        if total_costos:
            total_costos.actualizar_total()

class Total_Costos_Indirectos(models.Model):
    id = models.AutoField(primary_key=True)
    Anio = models.CharField(max_length=4)
    Mes = models.CharField(max_length=2)
    Total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    

    def __str__(self):
        return f"Año: {self.Anio}, Mes: {self.Mes}, Total: {self.Total}"

    class Meta:
        db_table = 'Total_Costos_Indirectos'
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes'], name='unique_total_costos_indirectos')
        ]
    def actualizar_total(self):
        """ Calcula la suma de los valores de los detalles asociados según Año y Mes. """
        total = Detalle_Costos_Indirectos.objects.filter(Anio=self.Anio, Mes=self.Mes).aggregate(
            total=models.Sum('Valor')
        )['total'] or 0
        self.Total = total
        self.save()

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
    PerfilId = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column='PerfilId', null=True, blank=True)
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

    # Campos ampliados
    GENERO_CHOICES = [('Masculino', 'Masculino'), ('Femenino', 'Femenino')]
    TIPO_CONTRATO_CHOICES = [('Indefinido', 'Indefinido'), ('Fijo', 'Fijo')]
    Genero = models.CharField(max_length=20, null=True, blank=True, choices=GENERO_CHOICES)
    EstadoCivil = models.CharField(max_length=50, null=True, blank=True)
    NumeroHijos = models.IntegerField(null=True, blank=True)
    TarjetaProfesional = models.BooleanField(null=True, blank=True)
    RH = models.CharField(max_length=10, null=True, blank=True)
    TipoContrato = models.CharField(max_length=20, null=True, blank=True, choices=TIPO_CONTRATO_CHOICES)
    FondoPension = models.CharField(max_length=100, null=True, blank=True)
    EPS = models.CharField(max_length=100, null=True, blank=True)
    FondoCesantias = models.CharField(max_length=100, null=True, blank=True)
    CajaCompensacion = models.CharField(max_length=100, null=True, blank=True)

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
    Telefono = models.CharField(max_length=20)
    telefono_fijo = models.CharField(max_length=30, null=True, blank=True)
    correo = models.CharField(max_length=100, null=True, blank=True)
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
    fecha_Inicio = models.DateField(null=True, blank=True)
    fecha_Fin = models.DateField(null=True, blank=True)
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
        indexes = [
            models.Index(fields=['Anio', 'Mes']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['Anio', 'Mes'], name='unique_horas_habiles')
        ]


class Tarifa_Consultores(models.Model):
    id = models.AutoField(primary_key=True)
    documentoId = models.ForeignKey('Consultores', on_delete=models.CASCADE, db_column='documentoId')
    moduloId = models.ForeignKey('Modulo', on_delete=models.CASCADE, db_column='moduloId')
    anio = models.CharField(max_length=4, db_column='anio')
    mes = models.CharField(max_length=2, db_column='mes')
    clienteID = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='clienteID')
    valorHora = models.DecimalField(max_digits=10, decimal_places=2, db_column='valorHora', null= True, blank= True)
    valorDia = models.DecimalField(max_digits=10, decimal_places=2, db_column='valorDia', null= True, blank= True)
    valorMes = models.DecimalField(max_digits=10, decimal_places=2, db_column='valorMes', null= True, blank= True)
    monedaId = models.ForeignKey('moneda', on_delete=models.CASCADE, db_column='monedaId')
    iva = models.DecimalField(max_digits=10, decimal_places=2, db_column='iva', null=True, blank=True)
    rteFte = models.DecimalField(max_digits=10, decimal_places=2, db_column='rteFte', null=True, blank=True)

    def __str__(self):
        return f"id: {self.id}, DocumentoId: {self.documentoId}, Año: {self.anio}, Mes: {self.mes}, ClienteId: {self.clienteID}, ValorHora: {self.valorHora}, ValorDia: {self.valorDia}, ValorMes: {self.valorMes}, Moneda: {self.id}, IVA: {self.iva}, RteFte: {self.rteFte}"

    class Meta:
        db_table = 'Tarifa_Consultores'
        constraints = [
            models.UniqueConstraint( 
                fields=['id','documentoId', 'anio', 'mes', 'clienteID', 'moduloId'], 
                name='unique_tarifa_consultores'
            )
        ]

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
    Contrato = models.CharField(max_length=50,null=False,blank=False)  
    ContratoVigente = models.BooleanField(default=True)
    OC_Facturar =  models.BooleanField(default=True)
    Parafiscales =  models.BooleanField(default=True)
    HorarioServicio = models.TextField(null=True, blank=True)
    FechaFacturacion = models.TextField(null=True, blank=True)
    TipoFacturacion = models.TextField(null=True, blank=True)
    Observaciones = models.TextField(null=True, blank=True)
    Polizas = models.BooleanField(default=False)
    PolizasDesc = models.CharField(max_length=200,null=True,blank=True)
    ContratoValor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    IncluyeIvaValor = models.BooleanField(default=False)
    ContratoDesc = models.CharField(max_length=200,null=True,blank=True)
    ServicioRemoto = models.BooleanField(default=False)
    monedaId = models.ForeignKey('moneda', null=True, blank=True, on_delete=models.CASCADE, db_column='monedaId')

    class Meta:
        db_table = 'Clientes_Contratos'

    def __str__(self):
        return f"ContratoId:{self.ClientesContratosId} - Cliente: {self.ClienteId} - FechaInicio: {self.FechaInicio} - FechaFin: {self.FechaFin} - Contrato: {self.Contrato} - ContratoVigente: {self.ContratoVigente} - OC_Facturar: {self.OC_Facturar} - Parafiscales: {self.Parafiscales} - HorarioServicio: {self.HorarioServicio} - FechaFacturacion: {self.FechaFacturacion} - TipoFacturacion: {self.TipoFacturacion} - Observaciones: {self.Observaciones} - Polizas: {self.Polizas} - PolizasDesc: {self.PolizasDesc} - ContratoValor: {self.ContratoValor} - IncluyeIvaValor: {self.IncluyeIvaValor} - ContratoDesc: {self.ContratoDesc} - ServicioRemoto: {self.ServicioRemoto} - Moneda: {self.monedaId}"
    
    
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
    Valor_Horas = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    DiasFactura = models.FloatField(null=True, blank=True)
    Valor_Dias = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    MesFactura = models.IntegerField(null=True, blank=True)
    Valor_Meses = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    Bolsa = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    Valor_Bolsa = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    Valor = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
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
    NumeroOtroSi = models.CharField(max_length=20, null=False, blank=False) 
    ValorOtroSi = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
    ValorIncluyeIva = models.BooleanField(default = 0)
    Polizas = models.BooleanField(default=0)
    PolizasDesc = models.CharField(max_length=200,null=True,blank=True)
    FirmadoFlag = models.BooleanField(default=0)
    FirmadoCliente = models.BooleanField(default=0)
    monedaId = models.ForeignKey('moneda', on_delete=models.CASCADE, db_column='monedaId')
    Contrato = models.CharField(max_length=50,null=True,blank=True) 

    class Meta:
        db_table = 'Contratos_OtrosSi'
        unique_together = ('ClienteId', 'FechaInicio', 'Contrato')

    def __str__(self):
        return f"ContratoId:{self.ContratosOtrosSiId} - Cliente: {self.ClienteId} - FechaInicio: {self.FechaInicio} - FechaFin: {self.FechaFin} - NumeroOtroSi: {self.NumeroOtroSi} - ValorOtroSi: {self.ValorOtroSi} - ValorIncluyeIva: {self.ValorIncluyeIva} - Polizas: {self.Polizas} - PolizasDesc: {self.PolizasDesc} - FirmadoFlag: {self.FirmadoFlag} - FirmadoCliente: {self.FirmadoCliente}"

class Ind_Totales_Diciembre(models.Model):
    Id = models.AutoField(primary_key=True)
    Anio = models.IntegerField()
    Mes = models.IntegerField()
    LineaId = models.ForeignKey('Linea', on_delete=models.CASCADE, db_column='LineaId')
    ClienteId = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')
    Trabajado = models.DecimalField(max_digits=15, decimal_places=2)
    Facturado = models.DecimalField(max_digits=15, decimal_places=2)
    Costo = models.DecimalField(max_digits=15, decimal_places=2)
    ValorFacturado = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        db_table = 'Ind_Totales_Diciembre'
        constraints = [
            models.UniqueConstraint(
                fields=['Anio', 'Mes', 'LineaId', 'ClienteId'], 
                name='unique_ind_totales_diciembre'
            )
        ]

    def __str__(self):
        return f"Año {self.Anio} - Mes {self.Mes} - Cliente {self.ClienteId.Nombre_Cliente}"
    
class TipoPagare(models.Model):
    Tipo_PagareId = models.AutoField(primary_key=True, db_column='Tipo_PagareId')
    Desc_Tipo_Pagare = models.CharField(max_length=100, db_column='Desc_Tipo_Pagare')

    class Meta:
        db_table = 'Tipo_Pagare'

    def __str__(self):
        return self.Desc_Tipo_Pagare


class ActividadPagare(models.Model):
    Act_PagareId = models.IntegerField(primary_key=True, db_column='Act_PagareId', unique=True)
    Descripcion_Act = models.CharField(max_length=100, db_column='Descripcion_Act')

    class Meta:
        db_table = 'Actividades_Pagare'

    def __str__(self):
        return self.Descripcion_Act


class Pagare(models.Model):
    Pagare_Id = models.AutoField(primary_key=True, db_column='Pagare_Id')
    Documento = models.CharField(max_length=20)
    Fecha_Creacion_Pagare = models.DateField()
    Tipo_Pagare = models.ForeignKey(
        TipoPagare,
        on_delete=models.PROTECT,
        db_column='Tipo_PagareId',
        related_name='pagares'
    )
    Fecha_inicio_Condonacion = models.DateField(null=True, blank=True)
    Fecha_fin_Condonacion = models.DateField(null=True, blank=True)
    Meses_de_condonacion = models.IntegerField(null=True, blank=True)
    Valor_Pagare = models.DecimalField(max_digits=15, decimal_places=2)
    porcentaje_ejecucion = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    estado = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=150, default="Sin descripción")

    class Meta:
        db_table = 'Pagare'

    def __str__(self):
        return f"Pagare {self.Pagare_Id} – {self.Documento}"


class PagarePlaneado(models.Model):
    Pagare = models.ForeignKey(
        Pagare,
        on_delete=models.CASCADE,
        db_column='Pagare_Id',
        related_name='planeados'
    )
    Actividad = models.ForeignKey(
        ActividadPagare,
        on_delete=models.CASCADE,
        db_column='Act_PagareId',
        related_name='planeados'
    )
    Horas_Planeadas = models.IntegerField()

    class Meta:
        db_table = 'Pagare_Planeado'
        constraints = [
            models.UniqueConstraint(
                fields=['Pagare', 'Actividad'],
                name='unique_pagare_planeado'
            )
        ]

    def __str__(self):
        return f"{self.Pagare} → {self.Actividad}: {self.Horas_Planeadas}h planeadas"


class PagareEjecutado(models.Model):
    Pagare = models.ForeignKey(
        Pagare,
        on_delete=models.CASCADE,
        db_column='Pagare_Id',
        related_name='ejecutados'
    )
    Actividad = models.ForeignKey(
        ActividadPagare,
        on_delete=models.CASCADE,
        db_column='Act_PagareId',
        related_name='ejecutados'
    )
    Horas_Ejecutadas = models.IntegerField()

    class Meta:
        db_table = 'Pagare_Ejecutado'
        constraints = [
            models.UniqueConstraint(
                fields=['Pagare', 'Actividad'],
                name='unique_pagare_ejecutado'
            )
        ]

    def __str__(self):
        return f"{self.Pagare} → {self.Actividad}: {self.Horas_Ejecutadas}h ejecutadas"
    
class Facturacion_Consultores(models.Model):
    id = models.AutoField(primary_key=True)
    Anio = models.IntegerField(blank=True, null=True)
    Mes = models.IntegerField(blank=True, null=True)
    Documento = models.ForeignKey('Consultores', on_delete=models.CASCADE, db_column='Documento')
    Empresa = models.CharField(max_length=100, blank=True, null=True)
    LineaId = models.ForeignKey('Linea', on_delete=models.CASCADE, db_column='LineaId')
    Cta_Cobro = models.CharField(max_length=50)
    Periodo_Cobrado = models.CharField(max_length=100)
    Aprobado_Por = models.CharField(max_length=100, blank=True, null=True)
    Fecha_Cobro = models.DateField(blank=True, null=True)
    Fecha_Pago = models.DateField(blank=True, null=True)
    ClienteId = models.ForeignKey('Clientes', on_delete=models.CASCADE, db_column='ClienteId')
    ModuloId = models.ForeignKey('Modulo', on_delete=models.CASCADE, db_column='ModuloId')
    Horas = models.DecimalField(max_digits=10, decimal_places=2)
    Valor_Unitario = models.DecimalField(max_digits=10, decimal_places=2)
    Valor_Cobro = models.DecimalField(max_digits=12, decimal_places=2)
    IVA = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Valor_Neto = models.FloatField(blank=True, null=True)
    Retencion_Fuente = models.DecimalField(max_digits=10, decimal_places=2)
    Valor_Pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    Factura = models.CharField(max_length=100, blank=True, null=True)
    Valor_Fcta_Cliente = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    Fecha = models.DateField(blank=True, null=True)
    Deuda_Tecnica = models.TextField(blank=True, null=True)
    Factura_Pendiente = models.TextField(blank=True, null=True)
    Dif = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    Diferencia_Bruta = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    Observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Facturacion_Consultores'

    def __str__(self):
        return f"Facturación {self.id} - Año {self.Anio} - Mes {self.Mes} - Consultor {self.Documento} - Línea {self.Linea}"

class LoginAttempt(models.Model):
    """
    Modelo para registrar intentos de inicio de sesión fallidos
    """
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'login_attempts'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.email} - {self.timestamp} - {'Exitoso' if self.successful else 'Fallido'}"

class LineaClienteCentroCostos(models.Model):
    id = models.AutoField(primary_key=True)

    linea = models.ForeignKey(
        'Linea',
        on_delete=models.CASCADE,
        db_column='LineaId',
        related_name='clientes_centros',
    )

    cliente = models.ForeignKey(
        'Clientes',
        on_delete=models.CASCADE,
        db_column='ClienteId',
        related_name='lineas_centros',
    )

    # ✅ NUEVO: Modulo
    modulo = models.ForeignKey(
        'Modulo',
        on_delete=models.CASCADE,
        db_column='ModuloId',
        related_name='lineas_clientes_centros',
    )

    centro_costo = models.ForeignKey(
        'CentrosCostos',
        on_delete=models.CASCADE,
        db_column='CentroCostoId',
        related_name='lineas_clientes_modulos',
    )

    # ✅ “Nombres reconocibles” listos para retorno (sin reemplazar IDs)
    @property
    def linea_nombre(self):
        return getattr(self.linea, "Linea", str(self.linea))

    @property
    def cliente_nombre(self):
        return getattr(self.cliente, "Nombre_Cliente", str(self.cliente))

    @property
    def modulo_nombre(self):
        # Ajusta el campo real si tu tabla Modulo usa otro nombre
        return getattr(self.modulo, "Modulo", getattr(self.modulo, "Nombre", str(self.modulo)))

    @property
    def codigo_ceco(self):
        return getattr(self.centro_costo, "codigoCeCo", str(self.centro_costo))

    def __str__(self):
        return f"{self.linea_nombre} | {self.cliente_nombre} | {self.modulo_nombre} | {self.codigo_ceco}"

    class Meta:
        db_table = 'Linea_Cliente_CentroCostos'
        constraints = [
            models.UniqueConstraint(
                fields=['linea', 'cliente', 'modulo', 'centro_costo'],
                name='uniq_linea_cliente_modulo_centrocosto'
            )
        ]
        indexes = [
            models.Index(fields=['linea'], name='idx_lcccm_linea'),
            models.Index(fields=['cliente'], name='idx_lcccm_cliente'),
            models.Index(fields=['modulo'], name='idx_lcccm_modulo'),
            models.Index(fields=['centro_costo'], name='idx_lcccm_centrocosto'),
            models.Index(fields=['linea', 'cliente', 'modulo'], name='idx_lcccm_lcm'),
        ]