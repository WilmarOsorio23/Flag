#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Render usará DJANGO_SETTINGS_MODULE desde env vars
python manage.py collectstatic --noinput
python manage.py migrate --noinput
