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
    monkeypatch.setitem(sys.modules, "llama_index", None)
    monkeypatch.setitem(sys.modules, "llama_index.llms", None)
    monkeypatch.setitem(sys.modules, "llama_index.llms.google_genai", None)

    sys.modules.pop("postgres_rag", None)
    postgres_rag = importlib.import_module("postgres_rag")

    with pytest.raises(ImportError, match="requirements-ai.txt"):
        postgres_rag.PostgresRAGEngine("postgres_test_project")

    sys.modules.pop("postgres_rag", None)