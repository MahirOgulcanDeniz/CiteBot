"""Shared test setup.

No test in this suite talks to OpenAI or any other paid API. Embeddings and the
LLM are replaced with local fakes, so running the tests is free and does not
need a real API key.
"""
import importlib
import os
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

FAKE_ANSWER = "Bu sahte bir cevaptır."


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    """Imports the real backend modules with fake embeddings and a fake LLM.

    Everything runs inside a temporary working directory, so the tests never
    touch your real uploads/ folder or your real vector database.
    """
    workdir = tmp_path_factory.mktemp("citebot_workdir")
    old_cwd = Path.cwd()
    os.chdir(workdir)

    mp = pytest.MonkeyPatch()
    mp.setenv("LLM_PROVIDER", "openai")
    mp.setenv("OPENAI_API_KEY", "test-key-not-real")

    prompts: list[str] = []

    def fake_llm(prompt_value):
        # Record the full prompt so tests can check what would be sent to a model
        prompts.append(prompt_value.to_string())
        return AIMessage(content=FAKE_ANSWER)

    import providers

    mp.setattr(providers, "get_embeddings", lambda: DeterministicFakeEmbedding(size=64))
    mp.setattr(providers, "get_llm", lambda: RunnableLambda(fake_llm))

    ingest = importlib.import_module("ingest")
    rag = importlib.import_module("rag")
    main = importlib.import_module("main")

    yield SimpleNamespace(
        ingest=ingest,
        rag=rag,
        main=main,
        prompts=prompts,
        workdir=workdir,
        fake_answer=FAKE_ANSWER,
    )

    os.chdir(old_cwd)
    mp.undo()


@pytest.fixture
def prompts(app):
    """List of prompts sent to the fake LLM, cleared before each test."""
    app.prompts.clear()
    return app.prompts


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient

    return TestClient(app.main.app)


@pytest.fixture
def make_txt(tmp_path):
    """Creates a UTF-8 text file and returns its path."""

    def _make(name="notes.txt", text="Merhaba dünya"):
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        return path

    return _make


@pytest.fixture
def ingest_text(app, make_txt):
    """Ingests a text document and returns (doc_id, stored_source_name)."""

    def _ingest(text, name="doc.txt"):
        doc_id = str(uuid.uuid4())
        path = make_txt(name, text)
        app.ingest.ingest_file(str(path), doc_id)
        return doc_id, path.name

    return _ingest