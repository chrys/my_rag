"""Helpers for optional runtime-only dependencies."""

from __future__ import annotations

import importlib
from typing import Any


class LazyModuleProxy:
    """Load an optional module only when one of its attributes is accessed."""

    def __init__(self, module_name: str, missing_dependency_message: str):
        self._module_name = module_name
        self._missing_dependency_message = missing_dependency_message

    def _load_module(self):
        try:
            return importlib.import_module(self._module_name)
        except ModuleNotFoundError as exc:
            raise RuntimeError(self._missing_dependency_message) from exc

    def __getattr__(self, attribute_name: str) -> Any:
        return getattr(self._load_module(), attribute_name)