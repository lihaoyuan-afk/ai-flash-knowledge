import asyncio
from google import genai
from google.genai import types

from app.models import ImageAnswer
from app.utils import clean_tags, extract_json_object


class ImageAnswerClient:
    def __init__(self, project: str | None, location: str, model: str) -> None:
        self.project = project
        self.location = location
        self.model = model

    async def answer(self, image_bytes: bytes, mime_type: str, caption: str | None = None) -> ImageAnswer:
        if not self.project:
            raise RuntimeError("VERTEX_AI_PROJECT is not configured")
        return await asyncio.to_thread(self._answer_sync, image_bytes, mime_type, caption)

    def _answer_sync(self, image_bytes: bytes, mime_type: str, caption: str | None = None) -> ImageAnswer:
        client = genai.Client(
            vertexai=True,
            project=self.project,
            location=self.location,
            http_options=types.HttpOptions(api_version="v1"),
        )
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

        response = client.models.generate_content(
            model=self.model,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
        data = extract_json_object(response.text or "{}")
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
