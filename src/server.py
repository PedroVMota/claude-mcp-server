from mcp.server.fastmcp import FastMCP

from src.handlers.repo_handler import (
    handle_create_repository,
    handle_delete_repository,
    handle_list_repositories,
    handle_remove_github_token,
    handle_set_github_token,
)

mcp = FastMCP(
    "claude-repo-manager",
    instructions=(
        "MCP server for managing GitHub repositories. "
        "Before using repo tools, store a GitHub token with 'set_github_token'. "
        "The token is encrypted and stored securely on disk."
    ),
)


@mcp.tool()
def set_github_token(token: str) -> str:
    """Store a GitHub Personal Access Token securely.

    The token is encrypted at rest using the server's encryption key.
    Required scopes: repo, delete_repo.
    """
    return handle_set_github_token(token)


@mcp.tool()
def remove_github_token() -> str:
    """Remove the stored GitHub token from the server."""
    return handle_remove_github_token()


@mcp.tool()
def list_repositories() -> str:
    """List all GitHub repositories for the authenticated user."""
    return handle_list_repositories()


@mcp.tool()
def create_repository(
    name: str, description: str = "", private: bool = True
) -> str:
    """Create a new GitHub repository.

    Args:
        name: Repository name.
        description: Optional description for the repository.
        private: Whether the repository should be private (default: True).
    """
    return handle_create_repository(
        name=name, description=description, private=private
    )


@mcp.tool()
def delete_repository(name: str) -> str:
    """Delete a GitHub repository. This action is irreversible.

    Args:
        name: Name of the repository to delete.
    """
    return handle_delete_repository(name=name)
