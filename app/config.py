from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    public_base_url: str | None = None

    telegram_bot_token: str | None = None
    telegram_allowed_user_ids: str | None = None

    notion_token: str | None = None
    notion_database_id: str | None = None

    llm_api_key: str | None = None
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"

    transcription_api_key: str | None = None
    transcription_base_url: str | None = None
    transcription_model: str | None = None

    notion_version: str = Field(default="2022-06-28")

    @property
    def allowed_user_ids(self) -> set[int]:
        if not self.telegram_allowed_user_ids:
            return set()
        return {
            int(item.strip())
            for item in self.telegram_allowed_user_ids.split(",")
            if item.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
