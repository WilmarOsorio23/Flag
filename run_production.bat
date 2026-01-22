@echo off
set ENV_FILE=C:\FlagsSecrets\sistema\.env.production
set DJANGO_SETTINGS_MODULE=sistema.settings.production
python manage.py runserver
