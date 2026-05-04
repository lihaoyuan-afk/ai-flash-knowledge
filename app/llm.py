import httpx

from app.models import AIExtraction
from app.utils import clean_tags, extract_json_object


class LLMClient:
    def __init__(self, api_key: str | None, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def extract(self, content: str) -> AIExtraction:
        if not self.api_key:
            return AIExtraction(
                title="待整理闪念",
                summary="AI 未配置，已先保存原文。",
                tags=["待整理"],
            )

        prompt = (
            "请根据以下内容，提取一个10字以内的中文标题、一段50字以内的中文摘要，"
            "以及最多3个中文标签。只输出严格 JSON，不要 Markdown，不要解释。"
            '格式：{"title":"","summary":"","tags":[]}\n\n'
            f"内容：{content}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个个人知识库整理助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()

        message = response.json()["choices"][0]["message"]["content"]
        data = extract_json_object(message)
        return AIExtraction(
            title=str(data.get("title") or "未命名闪念")[:80],
            summary=str(data.get("summary") or ""),
            tags=clean_tags(data.get("tags")),
        )
