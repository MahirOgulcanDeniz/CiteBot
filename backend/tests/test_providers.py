import importlib.util
from pathlib import Path

import pytest

PROVIDERS_FILE = Path(__file__).resolve().parent.parent / "providers.py"


def load_providers(monkeypatch, provider):
    """Loads a fresh copy of providers.py with the given LLM_PROVIDER."""
    monkeypatch.setenv("LLM_PROVIDER", provider)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")
    spec = importlib.util.spec_from_file_location("providers_under_test", PROVIDERS_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_openai_provider_builds_openai_objects(monkeypatch):
    module = load_providers(monkeypatch, "openai")
    assert type(module.get_embeddings()).__name__ == "OpenAIEmbeddings"
    assert type(module.get_llm()).__name__ == "ChatOpenAI"


def test_ollama_provider_builds_ollama_objects(monkeypatch):
    module = load_providers(monkeypatch, "ollama")
    assert type(module.get_embeddings()).__name__ == "OllamaEmbeddings"
    assert type(module.get_llm()).__name__ == "ChatOllama"


def test_provider_name_is_case_insensitive(monkeypatch):
    module = load_providers(monkeypatch, "OpenAI")
    assert module.PROVIDER == "openai"


def test_invalid_provider_raises_a_clear_error(monkeypatch):
    module = load_providers(monkeypatch, "banana")
    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        module.get_llm()
    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        module.get_embeddings()