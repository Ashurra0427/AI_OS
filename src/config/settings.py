"""Application settings loaded from environment and config files."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "JARVIS-AI-OS"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    data_dir: Path = Path.home() / ".jarvis"
    cache_dir: Path = Path.home() / ".jarvis" / "cache"
    models_dir: Path = Path.home() / ".jarvis" / "models"

    eventbus_bind: str = "tcp://127.0.0.1:5555"
    eventbus_connect: str = "tcp://127.0.0.1:5556"

    mcp_gateway_host: str = "127.0.0.1"
    mcp_gateway_port: int = 8765

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "sqlite+aiosqlite:///./jarvis.db"

    llm_cloud_provider: str = "openai"
    llm_cloud_api_key: str | None = None
    llm_local_model: str = "Qwen/Qwen2.5-0.5B-Instruct"
    llm_fallback_model: str = "Qwen/Qwen2.5-0.5B-Instruct"

    stt_cloud_provider: str = "groq"
    stt_cloud_api_key: str | None = None
    stt_local_model: str = "openai/whisper-tiny"

    tts_cloud_provider: str = "edge"
    tts_local_model: str = "hexgrad/Kokoro-82M"

    search_api_key: str | None = None
    search_api_url: str = "https://api.tavily.com/search"

    email_provider: str = "gmail"
    email_api_key: str | None = None

    jwt_secret_key: str = "change-me-in-production-use-env-var"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for d in (self.data_dir, self.cache_dir, self.models_dir):
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
