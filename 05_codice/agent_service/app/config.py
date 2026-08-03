from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione dell'Agent Service."""

    service_name: str = "WLDT LLM Agent Service"
    service_version: str = "0.1.0"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    persistence_service_base_url: str = "http://localhost:8081"
    openapi_spec_url: str = "http://localhost:8081/openapi.yaml"

    request_timeout_seconds: float = Field(default=120.0, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Restituisce una singola istanza della configurazione."""

    return Settings()