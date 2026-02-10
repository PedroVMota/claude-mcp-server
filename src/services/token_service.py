import os
from pathlib import Path

from src.utils.crypto import decrypt, encrypt

DEFAULT_TOKEN_DIR = Path.home() / ".claude-mcp"
DEFAULT_TOKEN_FILE = "token.enc"


def _token_path() -> Path:
    custom = os.environ.get("MCP_TOKEN_PATH")
    if custom:
        return Path(custom)
    return DEFAULT_TOKEN_DIR / DEFAULT_TOKEN_FILE


def store_token(token: str) -> Path:
    path = _token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encrypt(token))
    path.chmod(0o600)
    return path


def load_token() -> str:
    path = _token_path()
    if not path.exists():
        raise FileNotFoundError(
            "No GitHub token stored. Use the 'set_github_token' tool to store one."
        )
    return decrypt(path.read_bytes())


def delete_token() -> bool:
    path = _token_path()
    if path.exists():
        path.unlink()
        return True
    return False
