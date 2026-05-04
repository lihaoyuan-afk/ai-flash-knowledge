import httpx

from app.models import IncomingContent, SourceType
from app.utils import first_url


class TelegramClient:
    def __init__(self, bot_token: str | None) -> None:
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}" if bot_token else None

    async def send_message(self, chat_id: int, text: str) -> None:
        if not self.base_url:
            return
        async with httpx.AsyncClient(timeout=15) as client:
            await client.post(f"{self.base_url}/sendMessage", json={"chat_id": chat_id, "text": text})

    async def get_file_url(self, file_id: str) -> str:
        if not self.base_url or not self.bot_token:
            raise RuntimeError("Telegram token is not configured")

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{self.base_url}/getFile", params={"file_id": file_id})
            response.raise_for_status()
        file_path = response.json()["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"

    async def download_file(self, file_id: str) -> tuple[bytes, str, str]:
        file_url = await self.get_file_url(file_id)
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(file_url)
            response.raise_for_status()
        content_type = response.headers.get("content-type") or "image/jpeg"
        return response.content, content_type, file_url


def parse_update(update: dict) -> IncomingContent | None:
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None

    chat = message.get("chat") or {}
    user = message.get("from") or {}
    chat_id = chat.get("id")
    if chat_id is None:
        return None

    voice = message.get("voice")
    if voice and voice.get("file_id"):
        return IncomingContent(
            chat_id=chat_id,
            user_id=user.get("id"),
            message_id=message.get("message_id"),
            voice_file_id=voice["file_id"],
            source_type=SourceType.audio,
        )

    photos = message.get("photo") or []
    if photos:
        largest_photo = max(photos, key=lambda item: item.get("file_size", 0))
        return IncomingContent(
            chat_id=chat_id,
            user_id=user.get("id"),
            message_id=message.get("message_id"),
            text=message.get("caption"),
            photo_file_id=largest_photo.get("file_id"),
            source_type=SourceType.image_question,
        )

    text = message.get("text") or message.get("caption")
    if text:
        url = first_url(text)
        return IncomingContent(
            chat_id=chat_id,
            user_id=user.get("id"),
            message_id=message.get("message_id"),
            text=text,
            source_url=url,
            source_type=SourceType.link if url else SourceType.text,
        )

    return None
