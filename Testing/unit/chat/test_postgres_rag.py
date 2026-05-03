import importlib
import sys
from pathlib import Path

import pytest


SRC_DIR = Path(__file__).resolve().parents[3] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def test_postgres_rag_engine_raises_without_optional_dependencies(monkeypatch):
    monkeypatch.setitem(sys.modules, "txtai", None)
    monkeypatch.setitem(sys.modules, "txtai.embeddings", None)
    monkeypatch.setitem(sys.modules, "google", None)
    monkeypatch.setitem(sys.modules, "google.genai", None)

    sys.modules.pop("postgres_rag", None)
    postgres_rag = importlib.import_module("postgres_rag")

    with pytest.raises(ImportError, match="pip install google-genai"):
        postgres_rag.PostgresRAGEngine("postgres_test_project")

    sys.modules.pop("postgres_rag", None)


def test_postgres_rag_engine_raises_without_google_api_key(monkeypatch):
    class FakeEmbeddings:
        def __init__(self, config):
            self.config = config

    class FakeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key

    fake_google_types_module = type(
        "FakeGoogleTypesModule",
        (),
        {"GenerateContentConfig": object},
    )

    fake_google_genai_module = type(
        "FakeGoogleGenAIModule",
        (),
        {"Client": FakeClient, "types": fake_google_types_module},
    )

    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_pass")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setitem(sys.modules, "txtai", type("FakeTxtaiModule", (), {})())
    monkeypatch.setitem(
        sys.modules,
        "txtai.embeddings",
        type("FakeEmbeddingsModule", (), {"Embeddings": FakeEmbeddings})(),
    )
    monkeypatch.setitem(sys.modules, "google", type("FakeGoogleModule", (), {"genai": fake_google_genai_module})())
    monkeypatch.setitem(sys.modules, "google.genai", fake_google_genai_module)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_google_types_module)

    sys.modules.pop("postgres_rag", None)




def test_postgres_rag_engine_deletes_named_document_and_saves_index(monkeypatch, tmp_path):
    class FakeEmbeddings:
        def __init__(self, config):
            self.config = config
            self.deleted_ids = None
            self.saved_path = None

        def delete(self, ids):
            self.deleted_ids = ids

        def save(self, path):
            self.saved_path = path

    class FakeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key

    fake_google_types_module = type(
        "FakeGoogleTypesModule",
        (),
        {"GenerateContentConfig": object},
    )
    fake_google_genai_module = type(
        "FakeGoogleGenAIModule",
        (),
        {"Client": FakeClient, "types": fake_google_types_module},
    )

    monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_pass")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setitem(sys.modules, "txtai", type("FakeTxtaiModule", (), {})())
    monkeypatch.setitem(
        sys.modules,
        "txtai.embeddings",
        type("FakeEmbeddingsModule", (), {"Embeddings": FakeEmbeddings})(),
    )
    monkeypatch.setitem(sys.modules, "google", type("FakeGoogleModule", (), {"genai": fake_google_genai_module})())
    monkeypatch.setitem(sys.modules, "google.genai", fake_google_genai_module)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_google_types_module)

    sys.modules.pop("postgres_rag", None)
    postgres_rag = importlib.import_module("postgres_rag")
    monkeypatch.setattr(postgres_rag, "INDICES_DIR", tmp_path)

    engine = postgres_rag.PostgresRAGEngine("postgres_test_project")
    engine._content = [{"id": "doc.txt", "text": "foo"}]
    engine.delete_document("doc.txt")

    assert not any(d["id"] == "doc.txt" for d in engine._content)
    assert engine.content_path.exists()

    sys.modules.pop("postgres_rag", None)


def test_postgres_rag_engine_delete_project_artifacts_removes_index_directory(monkeypatch, tmp_path):
    class FakeEmbeddings:
        def __init__(self, config):
            self.config = config
            self.deleted_ids = None

        def delete(self, ids):
            self.deleted_ids = ids

        def load(self, path):
            self.loaded_path = path

    class FakeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key

    fake_google_types_module = type(
        "FakeGoogleTypesModule",
        (),
        {"GenerateContentConfig": object},
    )
    fake_google_genai_module = type(
        "FakeGoogleGenAIModule",
        (),
        {"Client": FakeClient, "types": fake_google_types_module},
    )

    monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_pass")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setitem(sys.modules, "txtai", type("FakeTxtaiModule", (), {})())
    monkeypatch.setitem(
        sys.modules,
        "txtai.embeddings",
        type("FakeEmbeddingsModule", (), {"Embeddings": FakeEmbeddings})(),
    )
    monkeypatch.setitem(sys.modules, "google", type("FakeGoogleModule", (), {"genai": fake_google_genai_module})())
    monkeypatch.setitem(sys.modules, "google.genai", fake_google_genai_module)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_google_types_module)

    sys.modules.pop("postgres_rag", None)
    postgres_rag = importlib.import_module("postgres_rag")
    monkeypatch.setattr(postgres_rag, "INDICES_DIR", tmp_path)

    index_dir = tmp_path / "postgres_test_project"
    index_dir.mkdir()
    (index_dir / "config").write_text("x", encoding="utf-8")

    engine = postgres_rag.PostgresRAGEngine("postgres_test_project")
    engine.delete_project_artifacts(["doc1.txt", "doc2.txt"])

    assert len(engine._content) == 0
    assert engine._embeddings.shape[0] == 0
    assert not index_dir.exists()

    sys.modules.pop("postgres_rag", None)