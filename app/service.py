import logging

from app.llm import LLMClient
from app.models import AIExtraction
from app.models import IncomingContent, KnowledgeItem, SourceType
from app.notion import NotionClient
from app.telegram import TelegramClient
from app.transcription import TranscriptionClient

logger = logging.getLogger(__name__)


class KnowledgeService:
    def __init__(
        self,
        telegram: TelegramClient,
        llm: LLMClient,
        notion: NotionClient,
        transcription: TranscriptionClient,
        allowed_user_ids: set[int],
    ) -> None:
        self.telegram = telegram
        self.llm = llm
        self.notion = notion
        self.transcription = transcription
        self.allowed_user_ids = allowed_user_ids

    async def handle(self, content: IncomingContent) -> KnowledgeItem | None:
        if self.allowed_user_ids and content.user_id not in self.allowed_user_ids:
            await self._safe_send(content.chat_id, "这个知识库暂时只允许主人使用。")
            return None

        try:
            item = await self._build_item(content)
            page_url = await self.notion.create_page(item)
        except Exception as exc:
            logger.exception("Failed to handle incoming content")
            await self._safe_send(content.chat_id, f"⚠️ 记录失败：{exc}")
            return None

        suffix = f"\n{page_url}" if page_url else "\nNotion 尚未配置，已完成本地处理。"
        await self._safe_send(content.chat_id, f"✅ 已成功存入知识库：{item.title}{suffix}")
        return item

    async def _safe_send(self, chat_id: int, text: str) -> None:
        try:
            await self.telegram.send_message(chat_id, text)
        except Exception:
            logger.exception("Failed to send Telegram message")
            return

    async def _build_item(self, content: IncomingContent) -> KnowledgeItem:
        text = content.text or ""
        status = "Success"

        if content.source_type == SourceType.audio:
            if not content.voice_file_id:
                raise ValueError("语音消息缺少文件 ID")
            audio_url = await self.telegram.get_file_url(content.voice_file_id)
            text = await self.transcription.transcribe_from_url(audio_url)
            text = f"🎙️ 音频输入\n\n{text}"

        if not text.strip():
            status = "Empty"

        try:
            extraction = await self.llm.extract(text)
        except Exception:
            status = "AI Failed"
            extraction = AIExtraction(
                title="待整理闪念",
                summary="AI 处理失败，已先保存原文。",
                tags=["待整理"],
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
