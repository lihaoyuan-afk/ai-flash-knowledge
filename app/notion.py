import httpx

from app.models import KnowledgeItem
from app.utils import chunk_text


class NotionClient:
    def __init__(self, token: str | None, database_id: str | None, notion_version: str) -> None:
        self.token = token
        self.database_id = database_id
        self.notion_version = notion_version

    async def create_page(self, item: KnowledgeItem) -> str | None:
        if not self.token or not self.database_id:
            return None

        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": item.title}}]},
                "Tags": {"multi_select": [{"name": tag} for tag in item.tags]},
                "Summary": {"rich_text": [{"text": {"content": item.summary[:1900]}}]},
                "Original Content": {
                    "rich_text": [{"text": {"content": part}} for part in chunk_text(item.original_content)]
                },
                "Type": {"select": {"name": item.source_type.value}},
                "Status": {"select": {"name": item.status}},
            },
        }

        if item.answer:
            payload["properties"]["Answer"] = {
                "rich_text": [{"text": {"content": part}} for part in chunk_text(item.answer)]
            }

        if item.source_url:
            payload["properties"]["Source URL"] = {"url": item.source_url}

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.notion_version,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("https://api.notion.com/v1/pages", json=payload, headers=headers)
            response.raise_for_status()

        return response.json().get("url")
