# Deployment

This document covers how to install, configure, and run claude-mcp-server locally and with Docker.

## Local Installation

```bash
# Clone the repository
git clone https://github.com/PedroVMota/claude-mcp-server.git
cd claude-mcp-server

# Install the package
pip install -e .

# Generate an encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set the encryption key
export MCP_ENCRYPTION_KEY="<your-generated-key>"
```

## Running the Server

### Standalone

```bash
python -m src.main
```

The server starts in **stdio transport** mode, communicating via standard input/output.

### With Claude Desktop

Add the following to your Claude Desktop configuration file (`claude_desktop_config.json`):

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

## Docker

### Image Details

The project uses a **multi-stage Docker build**:

| Stage | Base Image | Purpose |
|-------|-----------|---------|
| **Builder** | `python:3.11-slim` | Compiles dependencies (gcc, libffi-dev), creates venv, installs packages |
| **Runtime** | `python:3.11-slim` | Minimal image with only the venv copied from builder |

Security features:
- Runs as non-root user `mcp` (UID/GID 1000)
- No build tools in the runtime image
- Entrypoint: `claude-mcp`

### Running with Docker

```bash
# Pull the latest production image
docker pull ghcr.io/pedrovmota/claude-mcp-server:latest

# Run with encryption key
docker run -e MCP_ENCRYPTION_KEY="<your-key>" ghcr.io/pedrovmota/claude-mcp-server:latest
```

### Building Locally

```bash
docker build -t claude-mcp-server .
docker run -e MCP_ENCRYPTION_KEY="<your-key>" claude-mcp-server
```

## Docker Tags

Images are published to GitHub Container Registry (GHCR):

| Tag Pattern | When Created | Example |
|-------------|-------------|---------|
| `dev-X.Y.Z` | PR merged to `dev` | `ghcr.io/pedrovmota/claude-mcp-server:dev-0.2.0` |
| `X.Y.Z` | PR merged to `main` | `ghcr.io/pedrovmota/claude-mcp-server:0.2.0` |
| `latest` | PR merged to `main` | `ghcr.io/pedrovmota/claude-mcp-server:latest` |

Use `latest` for production. Use `dev-*` tags for testing pre-release versions.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MCP_ENCRYPTION_KEY` | Yes | — | Fernet encryption key for securing the GitHub token at rest |
| `MCP_TOKEN_PATH` | No | `~/.claude-mcp/token.enc` | Custom path for the encrypted token file |

### Generating an Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Store this key securely. If lost, you will need to generate a new key and re-store your GitHub token using the `set_github_token` tool.
