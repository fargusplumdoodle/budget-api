#!/bin/sh
set -e

until python scripts/wait-for-servers.py $DB_HOST:5432; do
  echo "Waiting for postgres to become available..."
  sleep 5
done

python manage.py makemigrations --noinput
python manage.py migrate --noinput

exec "$@"
