FROM rasa/rasa:2.8.21-full

COPY ./requirements-rasa.txt ./

USER root

RUN pip install -r requirements-rasa.txt

COPY . /app

USER 1001
