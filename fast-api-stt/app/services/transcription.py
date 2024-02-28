from functools import lru_cache

from fastapi import Depends

from models.stt import get_ml_model


class TranscriptionService:
    def __init__(self, model) -> None:
        self.stt_model = model
    
    def get_transcription(self, upload_name):
        transcription = self.stt_model.transcribe(upload_name)
        return transcription

@lru_cache()
def get_transcription_service(
    model = Depends(get_ml_model)
) -> TranscriptionService:
    return TranscriptionService(model)