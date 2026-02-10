#!/usr/bin/env python
r"""
Arregla el historial de migraciones cuando la BD tiene migraciones aplicadas
en otro orden (ej: admin antes que modulo). Ejecutar con ENV_FILE y
DJANGO_SETTINGS_MODULE definidos, o usa la ruta por defecto del .env.

Uso: python fix_migration_history.py
"""
import os
import sys
from pathlib import Path

# Cargar .env igual que manage.py
def load_dotenv_file(dotenv_path: Path) -> None:
    if not dotenv_path or not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)

env_file = os.environ.get("ENV_FILE", r"C:\FlagsSecrets\sistema\.env.development")
if env_file:
    load_dotenv_file(Path(env_file))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema.settings.development")

import django
django.setup()

from django.db import connection

def fix():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT applied FROM django_migrations WHERE app = %s AND name = %s",
            ["admin", "0001_initial"],
        )
        admin_row = cursor.fetchone()
        cursor.execute(
            "SELECT applied FROM django_migrations WHERE app = %s AND name = %s",
            ["modulo", "0001_initial"],
        )
        modulo_row = cursor.fetchone()

        if not modulo_row:
            # Insertar modulo.0001_initial con fecha anterior a la primera registrada
            cursor.execute("SELECT MIN(applied) FROM django_migrations")
            row = cursor.fetchone()
            min_applied = row[0] if row else None
            if min_applied:
                cursor.execute("SELECT DATE_SUB(%s, INTERVAL 1 DAY)", [min_applied])
                applied = cursor.fetchone()[0]
            else:
                applied = "2020-01-01 00:00:00"
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                ["modulo", "0001_initial", applied],
            )
            print("Registro modulo.0001_initial añadido. Ejecuta: python manage.py migrate")
            return

        if not admin_row:
            print("admin.0001_initial no está en el historial. Ejecuta migrate y si falla, revisa la BD.")
            return

        # Si modulo.0001_initial está aplicado *después* que admin, Django se queja. Ajustar orden.
        modulo_applied = modulo_row[0]
        admin_applied = admin_row[0]
        if modulo_applied >= admin_applied:
            cursor.execute(
                "SELECT DATE_SUB(%s, INTERVAL 1 DAY)", [admin_applied]
            )
            new_applied = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE django_migrations SET applied = %s WHERE app = %s AND name = %s",
                [new_applied, "modulo", "0001_initial"],
            )
            print("Fecha de modulo.0001_initial ajustada para que sea anterior a admin.")
        else:
            print("El orden ya es correcto (modulo antes que admin).")

    connection.commit()

    # Comprobar qué ve Django en la BD (por si usa otra BD o el app label es distinto)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT app, name, applied FROM django_migrations WHERE app IN ('modulo', 'admin', 'Modulo') ORDER BY applied"
        )
        rows = cursor.fetchall()
        print("Registros en django_migrations (modulo/admin):")
        for r in rows:
            print(f"  app={r[0]!r} name={r[1]!r} applied={r[2]}")
    print("Ejecuta: python manage.py migrate")

if __name__ == "__main__":
    fix()
