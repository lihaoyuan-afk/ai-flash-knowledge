import asyncio
import base64

import httpx
from google import genai
from google.genai import types

from app.models import ImageAnswer
from app.utils import clean_tags, extract_json_object


class ImageAnswerClient:
    def __init__(
        self,
        provider: str,
        vertex_project: str | None,
        vertex_location: str,
        vertex_model: str,
        xiaomi_api_key: str | None,
        xiaomi_base_url: str | None,
        xiaomi_model: str | None,
    ) -> None:
        self.provider = provider.lower().strip()
        self.vertex_project = vertex_project
        self.vertex_location = vertex_location
        self.vertex_model = vertex_model
        self.xiaomi_api_key = xiaomi_api_key
        self.xiaomi_base_url = xiaomi_base_url.rstrip("/") if xiaomi_base_url else None
        self.xiaomi_model = xiaomi_model

    async def answer(self, image_bytes: bytes, mime_type: str, caption: str | None = None) -> ImageAnswer:
        if self.provider == "xiaomi":
            return await self._answer_with_xiaomi(image_bytes, mime_type, caption)
        if self.provider == "vertex":
            return await asyncio.to_thread(self._answer_with_vertex_sync, image_bytes, mime_type, caption)
        raise RuntimeError(f"Unsupported image answer provider: {self.provider}")

    def _prompt(self, caption: str | None = None) -> str:
        prompt = (
            "You are a Chinese study assistant. The user sent an image that contains a question, "
            "exercise, screenshot, or problem. Read the image, infer the user's question, and answer it. "
            "Save-worthy output is the answer, not a description of the image. "
            "Return strict JSON only, with this schema: "
            '{"question":"","answer":"","title":"","summary":"","tags":[]}. '
            "question: OCR or concise restatement of the problem in the image. "
            "answer: complete answer in Chinese, with steps when useful. "
            "title: short Chinese title, <= 20 characters. "
            "summary: one-sentence Chinese summary, <= 80 characters. "
            "tags: up to 3 Chinese tags."
        )
        if caption:
            prompt += f"\nUser caption: {caption}"
        return prompt

    def _coerce_answer(self, raw_text: str) -> ImageAnswer:
        data = extract_json_object(raw_text or "{}")
        answer = str(data.get("answer") or "").strip()
        if not answer:
            answer = "The model did not produce an answer."

        return ImageAnswer(
            question=str(data.get("question") or "").strip(),
            answer=answer,
            title=str(data.get("title") or "Image answer")[:80],
            summary=str(data.get("summary") or "")[:500],
            tags=clean_tags(data.get("tags")),
        )

    def _answer_with_vertex_sync(self, image_bytes: bytes, mime_type: str, caption: str | None = None) -> ImageAnswer:
        if not self.vertex_project:
            raise RuntimeError("VERTEX_AI_PROJECT is not configured")

        client = genai.Client(
            vertexai=True,
            project=self.vertex_project,
            location=self.vertex_location,
            http_options=types.HttpOptions(api_version="v1"),
        )
        response = client.models.generate_content(
            model=self.vertex_model,
            contents=[
                self._prompt(caption),
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
        return self._coerce_answer(response.text or "{}")

    async def _answer_with_xiaomi(self, image_bytes: bytes, mime_type: str, caption: str | None = None) -> ImageAnswer:
        if not self.xiaomi_api_key:
            raise RuntimeError("XIAOMI_API_KEY is not configured")
        if not self.xiaomi_base_url:
            raise RuntimeError("XIAOMI_BASE_URL is not configured")
        if not self.xiaomi_model:
            raise RuntimeError("XIAOMI_MODEL is not configured")

        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        data_url = f"data:{mime_type};base64,{image_b64}"
        payload = {
            "model": self.xiaomi_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self._prompt(caption)},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.xiaomi_api_key}"}

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self.xiaomi_base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()

        raw_text = response.json()["choices"][0]["message"]["content"]
        return self._coerce_answer(raw_text)
