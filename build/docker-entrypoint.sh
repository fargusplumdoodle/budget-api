#!/bin/sh
set -e

CODE_DIR=/code

if [ -f $CODE_DIR/.env ]; then
  echo "Loading environment variables from $CODE_DIR/.env"
  set -a
  . $CODE_DIR/.env
  set +a
fi

until python $CODE_DIR/build/wait-for-servers.py $DB_HOST:5432; do
  echo "Waiting for postgres to become available..."
  sleep 2
done

python manage.py makemigrations --noinput
python manage.py migrate --noinput

exec "$@"
