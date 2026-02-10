import pytest
from cryptography.fernet import Fernet

from src.utils.crypto import decrypt, encrypt


@pytest.fixture(autouse=True)
def _setup_key(monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("MCP_ENCRYPTION_KEY", key)


def test_encrypt_decrypt_roundtrip():
    plaintext = "my-secret-token"
    ciphertext = encrypt(plaintext)
    assert decrypt(ciphertext) == plaintext


def test_encrypted_differs_from_plaintext():
    plaintext = "my-secret-token"
    ciphertext = encrypt(plaintext)
    assert ciphertext != plaintext.encode()


def test_decrypt_with_wrong_key(monkeypatch):
    ciphertext = encrypt("some-data")
    different_key = Fernet.generate_key().decode()
    monkeypatch.setenv("MCP_ENCRYPTION_KEY", different_key)
    with pytest.raises(RuntimeError, match="Failed to decrypt"):
        decrypt(ciphertext)


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("MCP_ENCRYPTION_KEY", raising=False)
    with pytest.raises(RuntimeError, match="MCP_ENCRYPTION_KEY"):
        encrypt("data")
