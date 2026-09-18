import importlib
import os
import sys
from unittest.mock import patch

import pytest


def reload_backend_config():
    sys.modules.pop("backend.config", None)
    import backend.config as config
    return importlib.reload(config)


def test_production_requires_secret_key():
    with patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "production",
            "DATABASE_URL": "postgresql://postgres:pass@db.example.com:5432/postgres",
            "SECRET_KEY": "",
            "FRONTEND_URL": "https://example.com",
        },
        clear=False,
    ):
        with pytest.raises(RuntimeError, match="SECRET_KEY must be configured in production"):
            reload_backend_config()
