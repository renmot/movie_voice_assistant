import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
import whisper

from api.v1.stt.views import router as stt_router
from models.stt import ml_models


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    ## Load the STT model
    ml_models["stt_model"] = whisper.load_model("tiny.en")
    logger.info('===STT model is loaded===')
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()
    logger.info('===STT model is deleted===')


app = FastAPI(
    lifespan=lifespan,
    title="STT API",
    description="API for STT",
    docs_url="/api/v1/stt/openapi",
    openapi_url="/api/v1/stt/openapi.json",
    version="1.0",
)


app.include_router(
    stt_router, prefix="/api/v1/stt", tags=["stt"]
)
