import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from TTS.api import TTS

from api.v1.tts.views import router as tts_router
from models.tts import ml_models


logger = logging.getLogger(__name__)


# If you use the XTTS model you need to agree to CPML license https://coqui.ai/cpml
os.environ["COQUI_TOS_AGREED"] = "1"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Load the TTS model
    ml_models["tts_model"] = TTS("tts_models/en/ljspeech/speedy-speech")
    logger.info('===TTS model is loaded===')
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()
    logger.info('===TTS model is deleted===')


app = FastAPI(
    lifespan=lifespan,
    title="TTS API",
    description="API for TTS",
    docs_url="/api/v1/tts/openapi",
    openapi_url="/api/v1/tts/openapi.json",
    version="1.0",
)


app.include_router(
    tts_router, prefix="/api/v1/tts", tags=["tts"]
)


