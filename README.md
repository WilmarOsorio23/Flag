# Configuración de Entornos Flag

Este proyecto tiene tres entornos configurados:
- Desarrollo (Development)
- Producción Local
- Producción

## 1. Entorno de Desarrollo (Por defecto)
Este es el entorno que se usa por defecto y se conecta a la base de datos de desarrollo.

Para ejecutar:
```bash
python manage.py runserver
```

Características:
- Base de datos: analisisdev
- Host: web.flagsoluciones.com
- URL: http://127.0.0.1:8000 o http://localhost:8000
- DEBUG: Activado

## 2. Entorno de Producción Local
Este entorno permite acceder a la base de datos de producción desde tu máquina local.

Para ejecutar:
```bash
run_local_production.bat
```

Características:
- Base de datos: analisisproduc (Base de datos de producción)
- Host: web.flagsoluciones.com
- URL: http://127.0.0.1:8000 o http://localhost:8000
- DEBUG: Activado
- Archivos estáticos servidos localmente

⚠️ **IMPORTANTE**:
- Este entorno se conecta directamente a la base de datos de producción
- Ten cuidado con los cambios que realices ya que afectarán a la base de datos real
- Se recomienda hacer un backup antes de realizar modificaciones importantes

## 3. Entorno de Producción
Este es el entorno que se ejecuta en el servidor de producción.

Características:
- Dominio: gif.flagsoluciones.com
- Base de datos: analisisproduc
- DEBUG: Desactivado
- SSL activado
- Archivos estáticos servidos desde el servidor

## Archivos Estáticos
Los archivos estáticos están configurados en:
```
os.path.join(BASE_DIR, 'Modulo', 'static')
```

## Logs
- Desarrollo: django_debug.log
- Producción Local: django_local_production.log
- Producción: django_production.log

## Requisitos
Asegúrate de tener instalados todos los paquetes necesarios:
```bash
pip install -r requirements.txt
```

## Solución de Problemas

### Si el servidor no inicia con la configuración correcta:
1. Verifica que estés usando el comando correcto para el entorno deseado
2. Asegúrate de que no haya variables de entorno conflictivas
3. Reinicia la terminal si es necesario

### Para verificar qué configuración está en uso:
- Al iniciar el servidor, verás un mensaje indicando qué configuración se está usando
- En el entorno de producción local, verás un mensaje con los detalles de la base de datos

## Contacto
Para cualquier duda o problema, contacta al equipo de desarrollo. 