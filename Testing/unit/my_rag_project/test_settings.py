import pytest
import os
from unittest import mock

def test_production_settings_strictness() -> None:
    """Ensure production settings do not have dev properties enabled."""
    with mock.patch.dict(os.environ, {
        "SECRET_KEY": "dummy-secret-key-for-testing",
        "DB_NAME": "test",
        "DB_USER": "test",
        "DB_PASSWORD": "test",
        "DB_HOST": "test"
    }):
        from src.apps.my_rag_project.settings import settings_prod

        assert settings_prod.DEBUG is False, "DEBUG should be False in production"
        assert getattr(settings_prod, "CORS_ALLOW_ALL_ORIGINS", False) is False, "CORS_ALLOW_ALL_ORIGINS should be False in production"

        # Test default secret key raises exception
        with mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="SECRET_KEY environment variable must be set and changed in production"):
                import importlib
                importlib.reload(settings_prod)
