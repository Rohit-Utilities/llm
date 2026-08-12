from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str

    zydit_api_key: str
    zydit_model: str
    zydit_base_url: str

    conversation_recent_messages: int = 8
    conversation_summary_max_tokens: int = 256

    max_output_tokens: int = 780
    request_timeout: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()