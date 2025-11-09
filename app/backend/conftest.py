import os
import secrets
import warnings

import pytest

# Ensure a secure SECRET_KEY is present for tests to avoid development fallback warnings
os.environ.setdefault("SECRET_KEY", secrets.token_hex(32))

# Filter out known deprecation warning originating from Starlette formparsers
warnings.filterwarnings(
    "ignore",
    category=PendingDeprecationWarning,
    module=r"starlette.formparsers",
)


@pytest.fixture(autouse=True)
def _ensure_secret_key_env(monkeypatch):
    # Ensure SECRET_KEY is available to any code that reads from os.environ
    monkeypatch.setenv("SECRET_KEY", os.environ["SECRET_KEY"])
    yield
