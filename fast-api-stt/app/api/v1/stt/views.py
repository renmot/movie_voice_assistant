import os
import shutil

from fastapi import APIRouter, Depends, UploadFile

from services.transcription import TranscriptionService, get_transcription_service


router = APIRouter()


UPLOAD_DIR="/tmp"


@router.get("/hc")
async def healthcheck():
    return "ok"


@router.post("/transcribe/")
async def transcribe(
    file: UploadFile,
    transcription_service: TranscriptionService = Depends(get_transcription_service)
) -> dict:

    filename = file.filename
    fileobj = file.file
    upload_name = os.path.join(UPLOAD_DIR, filename)
    upload_file = open(upload_name, 'wb+')
    shutil.copyfileobj(fileobj, upload_file)
    upload_file.close()

    transcription = transcription_service.get_transcription(upload_name)

    return transcription