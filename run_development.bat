@echo off
set ENV_FILE=C:\FlagsSecrets\sistema\.env.development
set DJANGO_SETTINGS_MODULE=sistema.settings.development
if "%~1"=="" (
    python manage.py runserver
) else (
    python manage.py %*
)
