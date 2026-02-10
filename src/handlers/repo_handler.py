import json

from src.services import github_service
from src.services.token_service import delete_token, store_token


def handle_set_github_token(token: str) -> str:
    path = store_token(token)
    return json.dumps({"success": True, "message": f"Token stored at {path}"})


def handle_remove_github_token() -> str:
    deleted = delete_token()
    if deleted:
        return json.dumps({"success": True, "message": "Token removed"})
    return json.dumps({"success": False, "message": "No token found to remove"})


def handle_list_repositories() -> str:
    repos = github_service.list_repositories()
    return json.dumps({"count": len(repos), "repositories": repos}, indent=2)


def handle_create_repository(
    name: str, description: str = "", private: bool = True
) -> str:
    repo = github_service.create_repository(
        name=name, description=description, private=private
    )
    return json.dumps({"success": True, "repository": repo}, indent=2)


def handle_delete_repository(name: str) -> str:
    result = github_service.delete_repository(name=name)
    return json.dumps({"success": True, **result}, indent=2)
