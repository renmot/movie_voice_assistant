FROM python:3.10

RUN apt-get update
RUN apt-get install gettext -y

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY requirements.txt requirements.txt

RUN  mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir


RUN groupadd -r dev && useradd -d /opt/app -r -g dev dev \
    && chown dev:dev -R /opt/app

COPY . .

COPY uwsgi/uwsgi.ini uwsgi.ini
COPY entrypoint.sh entrypoint.sh

RUN chmod +x ./entrypoint.sh

RUN chown -R dev:dev /opt/app

USER dev

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]