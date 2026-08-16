import pytest

from fitscorer.llm.provider import get_chat_model
from fitscorer.config import Settings


# Ollama
def test_get_model_ollama(monkeypatch):
    called_with = {}
    def fake_chat_ollama(**kwargs):
        called_with.update(kwargs)
        return "fake_ollama_instance"
    monkeypatch.setattr("fitscorer.llm.provider.ChatOllama", fake_chat_ollama)

    settings = Settings(llm_provider="ollama", ollama_model="llama3.2", ollama_base_url="http://localhost:11434")
    result = get_chat_model(settings)

    assert result == "fake_ollama_instance"
    assert called_with["model"] == "llama3.2"
    assert called_with["base_url"] == "http://localhost:11434"


def test_get_model_ollama_default_provider(monkeypatch):
    called_with = {}
    def fake_chat_ollama(**kwargs):
        called_with.update(kwargs)
        return "fake_ollama_instance"
    monkeypatch.setattr("fitscorer.llm.provider.ChatOllama", fake_chat_ollama)

    settings = Settings(_env_file=None)
    result = get_chat_model(settings)

    assert result == "fake_ollama_instance"
    assert called_with["model"] == settings.ollama_model
    assert called_with["base_url"] == settings.ollama_base_url


# Gemini
def test_get_model_gemini(monkeypatch):
    called_with = {}
    def fake_chat_gemini(**kwargs):
        called_with.update(kwargs)
        return "fake_gemini_instance"
    monkeypatch.setattr("fitscorer.llm.provider.ChatGemini", fake_chat_gemini)

    settings = Settings(llm_provider="gemini", gemini_model="gemini1.5", google_api_key="fake-api-key")
    result = get_chat_model(settings)

    assert result == "fake_gemini_instance"
    assert called_with["model"] == "gemini1.5"
    assert called_with["google_api_key"] == "fake-api-key"


# Invalid
def test_get_model_invalid():
    settings = Settings.model_construct(llm_provider="openai")

    with pytest.raises(ValueError):
        get_chat_model(settings)
