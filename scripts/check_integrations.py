import asyncio
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.llm import LLMClient


async def check_llm() -> tuple[bool, str]:
    settings = get_settings()
    if not settings.llm_api_key:
        return False, "LLM_API_KEY 未配置"

    client = LLMClient(settings.llm_api_key, settings.llm_base_url, settings.llm_model)
    result = await client.extract("今天学习了 FastAPI Webhook，想把灵感自动保存到 Notion。")
    if not result.title or not result.tags:
        return False, "LLM 返回内容不完整"
    return True, f"LLM 正常：{result.title} / {', '.join(result.tags)}"


async def check_notion() -> tuple[bool, str]:
    settings = get_settings()
    if not settings.notion_token or not settings.notion_database_id:
        return False, "NOTION_TOKEN 或 NOTION_DATABASE_ID 未配置"

    headers = {
        "Authorization": f"Bearer {settings.notion_token}",
        "Notion-Version": settings.notion_version,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"https://api.notion.com/v1/databases/{settings.notion_database_id}",
            headers=headers,
        )

    if response.status_code >= 400:
        return False, f"Notion 连接失败：HTTP {response.status_code}"
    payload = response.json()
    title_parts = payload.get("title") or []
    title = title_parts[0].get("plain_text") if title_parts else "未命名数据库"
    return True, f"Notion 正常：{title}"


async def check_telegram() -> tuple[bool, str]:
    settings = get_settings()
    if not settings.telegram_bot_token:
        return False, "TELEGRAM_BOT_TOKEN 未配置"

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe")

    if response.status_code >= 400:
        return False, f"Telegram 连接失败：HTTP {response.status_code}"
    payload = response.json()
    username = payload.get("result", {}).get("username", "unknown")
    return True, f"Telegram 正常：@{username}"


async def main() -> None:
    checks = [
        ("LLM", check_llm),
        ("Notion", check_notion),
        ("Telegram", check_telegram),
    ]

    failed = False
    for name, check in checks:
        try:
            ok, message = await check()
        except Exception as exc:
            ok, message = False, f"{type(exc).__name__}: {exc}"
        failed = failed or not ok
        icon = "OK" if ok else "MISSING"
        print(f"[{icon}] {name}: {message}")

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    asyncio.run(main())
