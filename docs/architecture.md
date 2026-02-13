# Architecture

This document describes the internal architecture of claude-mcp-server — how the components fit together, what each module does, and how data flows through the system.

## Overview

claude-mcp-server uses a layered architecture: an MCP server receives tool calls from Claude via stdio transport, delegates them to handler functions, which in turn call service modules for GitHub API operations and token management. Encryption utilities sit at the bottom layer.

## Component Diagram

```mermaid
flowchart TD
    subgraph Entry["Entry Point"]
        main["main.py\nmcp.run(transport='stdio')"]
    end

    subgraph Server["Server Layer"]
        server["server.py\nFastMCP('claude-repo-manager')\n5 @mcp.tool() definitions"]
    end

    subgraph Handlers["Handler Layer"]
        repo_handler["repo_handler.py\nhandle_set_github_token()\nhandle_remove_github_token()\nhandle_list_repositories()\nhandle_create_repository()\nhandle_delete_repository()"]
    end

    subgraph Services["Service Layer"]
        github_service["github_service.py\nGitHub API operations\nvia PyGithub"]
        token_service["token_service.py\nstore / load / delete token\nfile I/O with encryption"]
    end

    subgraph Utils["Utility Layer"]
        crypto["crypto.py\nFernet encrypt / decrypt\nkey from MCP_ENCRYPTION_KEY"]
    end

    subgraph Types["Type Definitions"]
        models["models.py\nSetTokenInput\nCreateRepoInput\nDeleteRepoInput"]
    end

    main --> server
    server --> repo_handler
    repo_handler --> github_service
    repo_handler --> token_service
    token_service --> crypto
    github_service -.-> token_service
```

## Module Responsibilities

| Module | Path | Responsibility |
|--------|------|----------------|
| `main.py` | `src/main.py` | Entry point. Starts the MCP server with stdio transport. |
| `server.py` | `src/server.py` | Defines the FastMCP instance and registers all 5 tools. |
| `repo_handler.py` | `src/handlers/repo_handler.py` | Handles tool calls, orchestrates service calls, formats JSON responses. |
| `github_service.py` | `src/services/github_service.py` | Interacts with the GitHub API via PyGithub. Manages client lifecycle. |
| `token_service.py` | `src/services/token_service.py` | Manages encrypted token storage on disk. Handles file paths and permissions. |
| `crypto.py` | `src/utils/crypto.py` | Provides Fernet-based encrypt/decrypt. Reads the encryption key from environment. |
| `models.py` | `src/types/models.py` | Pydantic models for tool input validation (`SetTokenInput`, `CreateRepoInput`, `DeleteRepoInput`). |

## Data Flow: Token Storage

When a user calls `set_github_token`, the token flows through the layers to be encrypted and stored on disk.

```mermaid
sequenceDiagram
    participant Claude
    participant Server as server.py
    participant Handler as repo_handler.py
    participant TokenSvc as token_service.py
    participant Crypto as crypto.py
    participant Disk as ~/.claude-mcp/token.enc

    Claude->>Server: set_github_token("ghp_...")
    Server->>Handler: handle_set_github_token(token)
    Handler->>TokenSvc: store_token(token)
    TokenSvc->>Crypto: encrypt(token)
    Crypto-->>TokenSvc: encrypted bytes
    TokenSvc->>Disk: write bytes (chmod 0600)
    TokenSvc-->>Handler: file path
    Handler-->>Server: JSON {"success": true}
    Server-->>Claude: result
```

## Data Flow: Repository Operation

When a user calls `list_repositories` (or `create_repository` / `delete_repository`), the token is decrypted from disk, used to authenticate with GitHub, and the result flows back.

```mermaid
sequenceDiagram
    participant Claude
    participant Server as server.py
    participant Handler as repo_handler.py
    participant GitHubSvc as github_service.py
    participant TokenSvc as token_service.py
    participant Crypto as crypto.py
    participant GitHub as GitHub API

    Claude->>Server: list_repositories()
    Server->>Handler: handle_list_repositories()
    Handler->>GitHubSvc: list_repositories()
    GitHubSvc->>TokenSvc: load_token()
    TokenSvc->>Crypto: decrypt(ciphertext)
    Crypto-->>TokenSvc: plaintext token
    TokenSvc-->>GitHubSvc: token
    GitHubSvc->>GitHub: GET /user/repos (authenticated)
    GitHub-->>GitHubSvc: repository list
    GitHubSvc-->>Handler: list[dict]
    Handler-->>Server: JSON response
    Server-->>Claude: result
```

## Module Relationships

```mermaid
classDiagram
    class main {
        +main()
    }
    class server {
        -mcp: FastMCP
        +set_github_token(token) str
        +remove_github_token() str
        +list_repositories() str
        +create_repository(name, description, private) str
        +delete_repository(name) str
    }
    class repo_handler {
        +handle_set_github_token(token) str
        +handle_remove_github_token() str
        +handle_list_repositories() str
        +handle_create_repository(name, description, private) str
        +handle_delete_repository(name) str
    }
    class github_service {
        -_client() Github
        +list_repositories() list~dict~
        +create_repository(name, description, private) dict
        +delete_repository(name) dict
    }
    class token_service {
        -_token_path() Path
        +store_token(token) Path
        +load_token() str
        +delete_token() bool
    }
    class crypto {
        +get_fernet() Fernet
        +encrypt(plaintext) bytes
        +decrypt(ciphertext) str
    }

    main --> server : starts
    server --> repo_handler : delegates
    repo_handler --> github_service : repo operations
    repo_handler --> token_service : token operations
    github_service --> token_service : loads token
    token_service --> crypto : encrypt/decrypt
```

## Code Distribution

```mermaid
pie title Lines of Code by Layer
    "Handlers (repo_handler)" : 36
    "Services (github_service)" : 68
    "Services (token_service)" : 40
    "Utils (crypto)" : 28
    "Server (server)" : 67
    "Entry (main)" : 10
    "Types (models)" : 16
```

## Dependencies

| Package | Version | Role |
|---------|---------|------|
| `mcp[cli]` | >= 1.2.0 | Model Context Protocol server framework |
| `PyGithub` | >= 2.1.1 | GitHub REST API client |
| `cryptography` | >= 42.0.0 | Fernet encryption for token-at-rest |
| `pydantic` | >= 2.0.0 | Data validation and model definitions |

### Dev Dependencies

| Package | Version | Role |
|---------|---------|------|
| `pytest` | >= 8.0.0 | Test framework |
| `pytest-asyncio` | >= 0.23.0 | Async test support |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MCP_ENCRYPTION_KEY` | Yes | — | Fernet encryption key for token storage |
| `MCP_TOKEN_PATH` | No | `~/.claude-mcp/token.enc` | Custom path for the encrypted token file |
