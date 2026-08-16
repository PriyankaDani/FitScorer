import pytest
from pydantic import ValidationError

from fitscorer.config import Settings


def test_defaults_match_env_example(monkeypatch):
    for var in ("LLM_PROVIDER", "OLLAMA_MODEL", "OLLAMA_BASE_URL", "GEMINI_MODEL", "GOOGLE_API_KEY"):
        monkeypatch.delenv(var, raising=False)

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "ollama"
    assert settings.ollama_model == "llama3.2:latest"
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.gemini_model == "gemini-1.5-flash"
    assert settings.google_api_key is None


def test_loads_ollama_provider_from_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:1b")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:9999")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "ollama"
    assert settings.ollama_model == "llama3.2:1b"
    assert settings.ollama_base_url == "http://localhost:9999"


def test_loads_gemini_provider_from_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-1.5-pro")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "gemini"
    assert settings.gemini_model == "gemini-1.5-pro"
    assert settings.google_api_key == "test-key"


def test_invalid_llm_provider_rejected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_llm_provider_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("llm_provider", "gemini")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "gemini"
