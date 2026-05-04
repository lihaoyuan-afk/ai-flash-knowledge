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
                title="Pending note",
                summary="AI is not configured; original content was saved.",
                tags=["Pending"],
            )

        prompt = (
            "Extract a short Chinese title, a Chinese one-sentence summary, and up to 3 Chinese tags. "
            "Return strict JSON only, no Markdown, with this schema: "
            '{"title":"","summary":"","tags":[]}\n\n'
            f"Content: {content}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You organize personal knowledge base notes."},
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
            title=str(data.get("title") or "Untitled note")[:80],
            summary=str(data.get("summary") or ""),
            tags=clean_tags(data.get("tags")),
        )
