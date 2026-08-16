from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: Literal["ollama", "gemini"] = "ollama"
    ollama_model: str = "llama3.2:latest"
    ollama_base_url: str = "http://localhost:11434"
    gemini_model: str = "gemini-1.5-flash"
    google_api_key: Optional[str] = None
