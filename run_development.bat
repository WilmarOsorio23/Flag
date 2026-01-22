@echo off
set ENV_FILE=C:\FlagsSecrets\sistema\.env.development
set DJANGO_SETTINGS_MODULE=sistema.settings.development
python manage.py runserver
