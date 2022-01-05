FROM python:3.10-slim

RUN set -ex \
    && RUN_DEPS=" \
        postgresql-client \
 	build-essential \
    " \
    && apt-get update \
    && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /code/
WORKDIR /code/
ADD . /code/

RUN set -ex \
    && python3.10 -m venv /venv \
    && /venv/bin/pip install -U pip pipenv  \
    && /venv/bin/pipenv lock \
	--keep-outdated \
	--requirements > /requirements.txt \
    && /venv/bin/pip install -U pip install -r /requirements.txt \
    && apt-get -y auto-remove \
    && rm -rf /var/lib/apt/lists/*


EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=budget.settings
ENV SECRET_KEY='tmp'
ENV UWSGI_WSGI_FILE=budget/wsgi.py
ENV UWSGI_VIRTUALENV=/venv UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_HTTP_AUTO_CHUNKED=1 UWSGI_HTTP_KEEPALIVE=1 UWSGI_UID=1000 UWSGI_GID=2000 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy
ENV UWSGI_WORKERS=2 UWSGI_THREADS=4

ENTRYPOINT ["/code/build/docker-entrypoint.sh"]

CMD ["/venv/bin/uwsgi", "--show-config"]
