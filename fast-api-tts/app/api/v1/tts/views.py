from time import time_ns
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import FileResponse

from api.v1.tts.models import Message
from models.tts import ml_models

router = APIRouter()

@router.get("/hc")
async def healthcheck():
    return "ok"


@router.post("/")
async def synthesis(message: Message):
    current_time = time_ns()
    rand_uuid4 = uuid4()
    file_name = f"{current_time}_{rand_uuid4}.wav"

    tts_model = ml_models["tts_model"]
    print("===Run tts_to_file===")
    tts_model.tts_to_file(
        text=message.text,
        # If you use a multi-lingual voice cloning model (e.g. XTTS), you must set the target speaker_wav and language
        # speaker_wav="ml/audio/speaker/audio.wav",
        # language="en",
        file_path=f"ml/audio/output/{file_name}"
    )
    print("===Prepeared a .wav file===")

    return {"file_name": file_name}


@router.get("/{file_name}")
async def get_file(file_name: str):
    response = FileResponse(
        path=f"ml/audio/output/{file_name}",
        media_type="audio/wav"
    )
    return response

