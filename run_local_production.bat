@echo off
set DJANGO_ENV=local_production
set DJANGO_SETTINGS_MODULE=sistema.settings.local_production
python manage.py runserver 