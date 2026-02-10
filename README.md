# claude-mcp-server

MCP server for managing GitHub repositories via Claude. Stores your GitHub token encrypted on disk so Claude can manage repos without ever seeing the raw token.

## Tools

| Tool | Description |
|------|-------------|
| `set_github_token` | Store a GitHub PAT securely (encrypted at rest) |
| `remove_github_token` | Remove the stored token |
| `list_repositories` | List all repos for the authenticated user |
| `create_repository` | Create a new GitHub repository |
| `delete_repository` | Delete a GitHub repository |

## Setup

```bash
# Install
pip install -e .

# Generate an encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set the key as an environment variable
export MCP_ENCRYPTION_KEY="<generated-key>"
```

## Usage

### With Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "repo-manager": {
      "command": "python",
      "args": ["-m", "src.main"],
      "cwd": "/path/to/claude-mcp-server",
      "env": {
        "MCP_ENCRYPTION_KEY": "<your-key>"
      }
    }
  }
}
```

### Standalone

```bash
python -m src.main
```

## Token Security

- Tokens are encrypted using Fernet (AES-128-CBC) via the `cryptography` library
- The encryption key is provided via `MCP_ENCRYPTION_KEY` environment variable
- Encrypted token file is stored at `~/.claude-mcp/token.enc` with `0600` permissions
- Custom path can be set via `MCP_TOKEN_PATH` environment variable

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```
