from github import Auth, Github
from github.Repository import Repository

from src.services.token_service import load_token


def _client() -> Github:
    token = load_token()
    return Github(auth=Auth.Token(token))


def list_repositories() -> list[dict]:
    gh = _client()
    try:
        repos = gh.get_user().get_repos()
        return [
            {
                "name": repo.name,
                "full_name": repo.full_name,
                "private": repo.private,
                "url": repo.html_url,
                "description": repo.description or "",
                "language": repo.language or "",
                "default_branch": repo.default_branch,
            }
            for repo in repos
        ]
    finally:
        gh.close()


def create_repository(
    name: str,
    description: str = "",
    private: bool = True,
) -> dict:
    gh = _client()
    try:
        user = gh.get_user()
        repo: Repository = user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=True,
        )
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "private": repo.private,
            "url": repo.html_url,
            "description": repo.description or "",
            "default_branch": repo.default_branch,
        }
    finally:
        gh.close()


def delete_repository(name: str) -> dict:
    gh = _client()
    try:
        user = gh.get_user()
        repo = user.get_repo(name)
        full_name = repo.full_name
        repo.delete()
        return {"deleted": True, "full_name": full_name}
    finally:
        gh.close()
