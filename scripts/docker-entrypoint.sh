#!/bin/sh
set -e

/venv/bin/python manage.py makemigrations --noinput
/venv/bin/python manage.py migrate --noinput

exec "$@"
