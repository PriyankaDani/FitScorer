from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI as ChatGemini
from langchain_ollama import ChatOllama

from fitscorer.config import Settings


def get_chat_model(settings: Settings) -> BaseChatModel:
    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
        )
    if settings.llm_provider == "gemini":
        return ChatGemini(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
        )
    raise ValueError(f"Unsupported llm_provider: {settings.llm_provider!r}")
