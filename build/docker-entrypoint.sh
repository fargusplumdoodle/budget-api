#!/bin/sh
set -e

until python /code/build/wait-for-servers.py $DB_HOST:5432; do
  echo "Waiting for postgres to become available..."
  sleep 2
done

python manage.py makemigrations --noinput
python manage.py migrate --noinput

exec "$@"
