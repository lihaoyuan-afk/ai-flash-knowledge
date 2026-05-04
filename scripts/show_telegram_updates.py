import asyncio
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import get_settings


async def main() -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        print("TELEGRAM_BOT_TOKEN 未配置")
        raise SystemExit(1)

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"https://api.telegram.org/bot{settings.telegram_bot_token}/getUpdates")
        response.raise_for_status()

    updates = response.json().get("result", [])
    if not updates:
        print("还没有收到消息。请先在 Telegram 给 Bot 发一句话，然后再运行本脚本。")
        return

    for update in updates[-5:]:
        message = update.get("message") or update.get("edited_message") or {}
        sender = message.get("from") or {}
        chat = message.get("chat") or {}
        print(
            f"user_id={sender.get('id')} username={sender.get('username')} "
            f"chat_id={chat.get('id')} text={message.get('text')}"
        )


if __name__ == "__main__":
    asyncio.run(main())
