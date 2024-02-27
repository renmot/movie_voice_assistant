import os
import shutil

from fastapi import APIRouter, UploadFile

from models.stt import ml_models

router = APIRouter()


UPLOAD_DIR="/tmp"


@router.get("/hc")
async def healthcheck():
    return "ok"


@router.post("/transcribe/")
async def transcribe(file: UploadFile):
    stt_model = ml_models["stt_model"]

    filename = file.filename
    fileobj = file.file
    upload_name = os.path.join(UPLOAD_DIR, filename)
    upload_file = open(upload_name, 'wb+')
    shutil.copyfileobj(fileobj, upload_file)
    upload_file.close()
    
    result = stt_model.transcribe(upload_name)
    return result