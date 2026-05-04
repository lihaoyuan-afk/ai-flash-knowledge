import httpx


class TranscriptionClient:
    def __init__(self, api_key: str | None, base_url: str | None, model: str | None) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") if base_url else None
        self.model = model

    async def transcribe_from_url(self, audio_url: str) -> str:
        if not self.api_key or not self.base_url or not self.model:
            raise RuntimeError("语音转写服务尚未配置")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=60) as client:
            audio = await client.get(audio_url)
            audio.raise_for_status()
            files = {"file": ("telegram-audio.ogg", audio.content, "audio/ogg")}
            data = {"model": self.model}
            response = await client.post(f"{self.base_url}/audio/transcriptions", headers=headers, data=data, files=files)
            response.raise_for_status()

        payload = response.json()
        if "text" not in payload:
            raise ValueError("语音转写响应中没有 text 字段")
        return str(payload["text"])
