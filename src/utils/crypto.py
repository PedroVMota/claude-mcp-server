import os

from cryptography.fernet import Fernet, InvalidToken


def get_fernet() -> Fernet:
    key = os.environ.get("MCP_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError(
            "MCP_ENCRYPTION_KEY environment variable is not set. "
            "Generate one with: python -c "
            "\"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def encrypt(plaintext: str) -> bytes:
    return get_fernet().encrypt(plaintext.encode())


def decrypt(ciphertext: bytes) -> str:
    try:
        return get_fernet().decrypt(ciphertext).decode()
    except InvalidToken as exc:
        raise RuntimeError(
            "Failed to decrypt token. Check that MCP_ENCRYPTION_KEY is correct."
        ) from exc
