import logging
import requests
import urllib
from sanic import Blueprint, response
from socketio import AsyncServer
from typing import Optional, Text, Any

from rasa.core.channels.channel import InputChannel
from rasa.core.channels.channel import UserMessage, OutputChannel


logger = logging.getLogger(__name__)


class SocketBlueprint(Blueprint):
    def __init__(self, sio: AsyncServer, socketio_path, *args, **kwargs):
        self.sio = sio
        self.socketio_path = socketio_path
        super(SocketBlueprint, self).__init__(*args, **kwargs)

    def register(self, app, options):
        self.sio.attach(app, self.socketio_path)
        super(SocketBlueprint, self).register(app, options)


class SocketIOOutput(OutputChannel):

    @classmethod
    def name(cls):
        return "socketio"

    def __init__(self, sio, sid, bot_message_evt, message):
        self.sio = sio
        self.sid = sid
        self.bot_message_evt = bot_message_evt
        self.message = message


    async def _send_audio_message(self, socket_id, response,  **kwargs: Any):
        """Sends a message to the recipient using the bot event."""

        response_text = response['text']
        data={"text": response_text}

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        logger.debug("===Send request to tts===")
        r = requests.post('http://tts-api:8001/api/v1/tts/', json=data, headers=headers)
        logger.debug("===Got response from tts===")

        r_dict = r.json()
        OUT_FILE = r_dict["file_name"]
        link = f"http://127.0.0.1:80/api/v1/tts/{OUT_FILE}"
        logger.debug(f"link: {link}")

        logger.debug(f"message: 'text':{response_text}, 'link':{link}")
        await self.sio.emit(self.bot_message_evt, {'text':response_text, "link":link}, room=socket_id)
        logger.debug(f"message after: 'text':{response_text}, 'link':{link}, 'room':{socket_id}")


    async def send_text_message(self, recipient_id: Text, message: Text, **kwargs: Any) -> None:
        """Send a message through this channel."""

        await self._send_audio_message(self.sid, {"text": message})


class SocketIOInput(InputChannel):
    """A socket.io input channel."""

    @classmethod
    def name(cls):
        return "socketio"

    @classmethod
    def from_credentials(cls, credentials):
        credentials = credentials or {}
        return cls(credentials.get("user_message_evt", "user_uttered"),
                   credentials.get("bot_message_evt", "bot_uttered"),
                   credentials.get("namespace"),
                   credentials.get("session_persistence", False),
                   credentials.get("socketio_path", "/socket.io"),
                   )

    def __init__(self,
                 user_message_evt: Text = "user_uttered",
                 bot_message_evt: Text = "bot_uttered",
                 namespace: Optional[Text] = None,
                 session_persistence: bool = False,
                 socketio_path: Optional[Text] = '/socket.io'
                 ):
        self.bot_message_evt = bot_message_evt
        self.session_persistence = session_persistence
        self.user_message_evt = user_message_evt
        self.namespace = namespace
        self.socketio_path = socketio_path


    def blueprint(self, on_new_message):
        sio = AsyncServer(
            async_mode="sanic",
            cors_allowed_origins=[],
            ping_timeout=20000,
            ping_interval=250
        )
        socketio_webhook = SocketBlueprint(
            sio, self.socketio_path, "socketio_webhook", __name__
        )

        @socketio_webhook.route("/", methods=['GET'])
        async def health(request):
            return response.json({"status": "ok"})

        @sio.on('connect', namespace=self.namespace)
        async def connect(sid, environ):
            logger.debug("User {} connected to socketIO endpoint.".format(sid))

        @sio.on('disconnect', namespace=self.namespace)
        async def disconnect(sid):
            logger.debug("User {} disconnected from socketIO endpoint."
                         "".format(sid))

        @sio.on('session_request', namespace=self.namespace)
        async def session_request(sid, data):
            logger.debug(f"sid: {sid}, data: {data}")
            await sio.emit("session_confirm", sid, room=sid)
            logger.debug("User {} connected to socketIO endpoint."
                         "".format(sid))

        @sio.on('user_uttered', namespace=self.namespace)
        async def handle_message(sid, data):

            output_channel = SocketIOOutput(sio, sid, self.bot_message_evt, data['message'])
            if data['message'] == "/get_started":
                message = data['message']
            else:
                # receive audio
                received_file = 'output_'+sid+'.wav'

                urllib.request.urlretrieve(data['message'], received_file)

                files = {"file": open("output_{0}.wav".format(sid), 'rb')}
                r = requests.post('http://stt-api:8002/api/v1/stt/transcribe/', files=files)
                r_dict = r.json()
                message = r_dict['text']

                logger.debug(f"message: {message}")
                await sio.emit(self.user_message_evt, {"text":message}, room=sid)


            message_rasa = UserMessage(message, output_channel, sid,
                                  input_channel=self.name())
            await on_new_message(message_rasa)

        return socketio_webhook
