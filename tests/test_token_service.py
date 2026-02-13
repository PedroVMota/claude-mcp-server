import os
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from src.services.token_service import delete_token, load_token, store_token


@pytest.fixture(autouse=True)
def _setup_env(tmp_path, monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("MCP_ENCRYPTION_KEY", key)
    token_path = tmp_path / "token.enc"
    monkeypatch.setenv("MCP_TOKEN_PATH", str(token_path))


def test_store_and_load_token():
    store_token("test-token-123")
    assert load_token() == "test-token-123"


def test_load_token_missing_raises():
    with pytest.raises(FileNotFoundError, match="No GitHub token stored"):
        load_token()


def test_store_token_file_permissions(tmp_path):
    path = store_token("test-token-secret")
    stat = os.stat(path)
    assert oct(stat.st_mode & 0o777) == "0o600"


def test_delete_token():
    store_token("test-token-to-delete")
    assert delete_token() is True
    with pytest.raises(FileNotFoundError):
        load_token()


def test_delete_token_when_missing():
    assert delete_token() is False


def test_roundtrip_preserves_special_chars():
    token = "t0ken-with.special/chars=+"
    store_token(token)
    assert load_token() == token
