import logging

from app.image_answer import ImageAnswerClient
from app.llm import LLMClient
from app.models import AIExtraction, IncomingContent, KnowledgeItem, SourceType
from app.notion import NotionClient
from app.telegram import TelegramClient
from app.transcription import TranscriptionClient

logger = logging.getLogger(__name__)


class KnowledgeService:
    def __init__(
        self,
        telegram: TelegramClient,
        llm: LLMClient,
        image_answer: ImageAnswerClient,
        notion: NotionClient,
        transcription: TranscriptionClient,
        allowed_user_ids: set[int],
    ) -> None:
        self.telegram = telegram
        self.llm = llm
        self.image_answer = image_answer
        self.notion = notion
        self.transcription = transcription
        self.allowed_user_ids = allowed_user_ids

    async def handle(self, content: IncomingContent) -> KnowledgeItem | None:
        if self.allowed_user_ids and content.user_id not in self.allowed_user_ids:
            await self._safe_send(content.chat_id, "This bot is private.")
            return None

        try:
            item = await self._build_item(content)
            page_url = await self.notion.create_page(item)
        except Exception as exc:
            logger.exception("Failed to handle incoming content")
            await self._safe_send(content.chat_id, f"Record failed: {exc}")
            return None

        suffix = f"\n{page_url}" if page_url else "\nNotion is not configured."
        await self._safe_send(content.chat_id, f"Saved: {item.title}{suffix}")
        return item

    async def _safe_send(self, chat_id: int, text: str) -> None:
        try:
            await self.telegram.send_message(chat_id, text)
        except Exception:
            logger.exception("Failed to send Telegram message")

    async def _build_item(self, content: IncomingContent) -> KnowledgeItem:
        text = content.text or ""
        status = "Success"

        if content.source_type == SourceType.audio:
            if not content.voice_file_id:
                raise ValueError("Audio message is missing file_id")
            audio_url = await self.telegram.get_file_url(content.voice_file_id)
            text = await self.transcription.transcribe_from_url(audio_url)
            text = f"Audio input\n\n{text}"

        if content.source_type == SourceType.image_question:
            if not content.photo_file_id:
                raise ValueError("Photo message is missing file_id")
            image_bytes, mime_type, image_url = await self.telegram.download_file(content.photo_file_id)
            result = await self.image_answer.answer(image_bytes, mime_type, content.text)
            return KnowledgeItem(
                title=result.title,
                summary=result.summary,
                tags=result.tags,
                original_content=result.question or content.text or "Image question",
                source_type=SourceType.image_question,
                source_url=image_url,
                answer=result.answer,
                status="Success",
            )

        if not text.strip():
            status = "Empty"

        try:
            extraction = await self.llm.extract(text)
        except Exception:
            logger.exception("Failed to extract text content")
            status = "AI Failed"
            extraction = AIExtraction(
                title="Pending note",
                summary="AI processing failed; original content was saved.",
                tags=["Pending"],
            )

        return KnowledgeItem(
            title=extraction.title,
            summary=extraction.summary,
            tags=extraction.tags,
            original_content=text,
            source_type=content.source_type,
            source_url=content.source_url,
            status=status,
        )
