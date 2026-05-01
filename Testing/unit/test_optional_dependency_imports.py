import builtins
import importlib
import sys

import pytest


OPTIONAL_GOOGLE_VIEW_MODULES = [
    "src.apps.documents.views",
    "src.apps.chat.views",
    "src.apps.projects.views",
]

OPTIONAL_LOCAL_RAG_VIEW_MODULES = [
    "src.apps.documents.views",
    "src.apps.chat.views",
]


@pytest.mark.parametrize("module_name", OPTIONAL_GOOGLE_VIEW_MODULES)
def test_view_modules_import_without_google_file_search(monkeypatch, module_name):
    real_import = builtins.__import__

    def blocking_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "google_file_search":
            raise ModuleNotFoundError("No module named 'google'")
        return real_import(name, globals, locals, fromlist, level)

    sys.modules.pop("google_file_search", None)
    sys.modules.pop(module_name, None)
    monkeypatch.setattr(builtins, "__import__", blocking_import)

    imported_module = importlib.import_module(module_name)

    assert imported_module is not None


@pytest.mark.parametrize("module_name", OPTIONAL_LOCAL_RAG_VIEW_MODULES)
def test_view_modules_import_without_local_rag(monkeypatch, module_name):
    real_import = builtins.__import__

    def blocking_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "local_rag":
            raise ModuleNotFoundError("No module named 'faiss'")
        return real_import(name, globals, locals, fromlist, level)

    sys.modules.pop("local_rag", None)
    sys.modules.pop(module_name, None)
    monkeypatch.setattr(builtins, "__import__", blocking_import)

    imported_module = importlib.import_module(module_name)

    assert imported_module is not None