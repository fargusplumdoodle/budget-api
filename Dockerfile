FROM python:3.10-slim

RUN set -ex \
    && RUN_DEPS=" \
        postgresql-client \
      	build-essential \
    " \
    && apt-get update \
    && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -y auto-remove


RUN mkdir /code/
WORKDIR /code/
ADD ./pyproject.toml /code/
ADD ./poetry.lock /code/

RUN set -ex \
    && pip install --upgrade pip  \
    && pip install -U "poetry==1.2.2"  \
    && poetry export -f requirements.txt --without-hashes \
        | pip install -r /dev/stdin

ADD . /code/
EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=budget.settings
ENV SECRET_KEY='tmp'
ENV UWSGI_WSGI_FILE=budget/wsgi.py
ENV UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_HTTP_AUTO_CHUNKED=1 UWSGI_HTTP_KEEPALIVE=1 UWSGI_UID=1000 UWSGI_GID=2000 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy
ENV UWSGI_WORKERS=2 UWSGI_THREADS=4

ENTRYPOINT ["/code/build/docker-entrypoint.sh"]

CMD ["uwsgi", "--show-config"]
