import logging
import sys

from fastapi import Depends, FastAPI, Request

from app.config import Settings, get_settings
from app.image_answer import ImageAnswerClient
from app.llm import LLMClient
from app.notion import NotionClient
from app.service import KnowledgeService
from app.telegram import TelegramClient, parse_update
from app.transcription import TranscriptionClient

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="AI Flash Knowledge Base", version="0.2.0")


def get_service(settings: Settings = Depends(get_settings)) -> KnowledgeService:
    return KnowledgeService(
        telegram=TelegramClient(settings.telegram_bot_token),
        llm=LLMClient(settings.llm_api_key, settings.llm_base_url, settings.llm_model),
        image_answer=ImageAnswerClient(
            settings.vertex_ai_project,
            settings.vertex_ai_location,
            settings.vertex_ai_model,
        ),
        notion=NotionClient(settings.notion_token, settings.notion_database_id, settings.notion_version),
        transcription=TranscriptionClient(
            settings.transcription_api_key,
            settings.transcription_base_url,
            settings.transcription_model,
        ),
        allowed_user_ids=settings.allowed_user_ids,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request, service: KnowledgeService = Depends(get_service)) -> dict[str, str]:
    update = await request.json()
    content = parse_update(update)
    if content is None:
        return {"status": "ignored"}

    await service.handle(content)
    return {"status": "ok"}
