FROM rasa/rasa-sdk:2.8.3

WORKDIR /app

COPY actions/requirements-actions.txt ./

USER root

RUN pip install -r requirements-actions.txt

COPY ./actions /app/actions

USER 1001
