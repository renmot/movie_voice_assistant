# Movie Voice Assistant

A simple voice assistants with:
- [Rasa](https://github.com/RasaHQ/rasa-demo)
- Django
- Elasticsearch
- [Voice Interface](https://github.com/RasaHQ/rasa-voice-interface)
- Speech to Text API
- Text to Speech API

The interface records the voice input by connecting to the microphone enabled on your browser and autoplays the response:
- Rasa and Rasa Voice Interface (VI) use a socket.
- Rasa sends an audio recevied from VI to the Speech to Text (STT) API.
- STT API transcribes the audio and returns a text to Rasa.
- Rasa applies a [model](./rasa/models/) to get an intent and sends the text to Rasa Actions.
- Rasa Actions:
  - Transforms the text to an Elasticsearch (ES) query.
  - Requests data from ES.
  - Transforms ES response to a message and returns it to Rasa.
- Rasa sends the message to the Text to Speech (TTS) API.
- TTS API synthesises an audio and returns it to Rasa.
- Rasa sends an audio to the socket.
- VI autoplays the audio for a user.

![alt text](./architecture/architecture.png?raw=true)

## How to run the project

The project requires 30GB free disk space (for full installation).

Create a .env file.
Add to the .env file:
- Django variable SECRET_KEY

Run docker-compose:
```
docker-compose up -d --build
```
Create Django superuser (Optional):
```
make admin
```

## Open in a browser
- Voice Assistant UI: http://127.0.0.1:8080/
- Speech to Text API: http://127.0.0.1:80/api/v1/stt/openapi
- Text to Speech API: http://127.0.0.1:80/api/v1/tts/openapi
- Django Admin panel: http://127.0.0.1:80/admin/

## Use cases

Currently Movie Voice Assistant can provide the following information:
- Movies filtered by one or multiple filters: genre, actor, director, rating.
- Additional information for one or multiple movies recevied in the first response: description, actor names, director name, genre, rating.

To extend scenarios, modify the [data](./rasa/data/) and [train](./rasa/README.md) a new model.