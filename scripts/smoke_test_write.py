import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.llm import LLMClient
from app.models import KnowledgeItem, SourceType
from app.notion import NotionClient


async def main() -> None:
    settings = get_settings()
    llm = LLMClient(settings.llm_api_key, settings.llm_base_url, settings.llm_model)
    notion = NotionClient(settings.notion_token, settings.notion_database_id, settings.notion_version)

    original = "联调测试：今天把 Telegram、LLM 和 Notion 三段链路接起来，准备做一个零摩擦闪念知识库。"
    extraction = await llm.extract(original)
    item = KnowledgeItem(
        title=f"联调测试-{extraction.title}",
        summary=extraction.summary,
        tags=extraction.tags,
        original_content=original,
        source_type=SourceType.text,
        status="Success",
    )
    page_url = await notion.create_page(item)
    print(f"写入成功：{page_url}")


if __name__ == "__main__":
    asyncio.run(main())
