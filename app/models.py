from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class SourceType(StrEnum):
    text = "Text"
    audio = "Audio"
    link = "Link"


class AIExtraction(BaseModel):
    title: str = Field(default="未命名闪念", max_length=80)
    summary: str = Field(default="")
    tags: list[str] = Field(default_factory=lambda: ["未分类"])


class KnowledgeItem(BaseModel):
    title: str
    summary: str
    tags: list[str]
    original_content: str
    source_type: SourceType
    source_url: str | None = None
    status: str = "Success"


class IncomingContent(BaseModel):
    chat_id: int
    user_id: int | None = None
    message_id: int | None = None
    text: str | None = None
    voice_file_id: str | None = None
    source_url: str | None = None
    source_type: SourceType
