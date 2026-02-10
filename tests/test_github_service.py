from unittest.mock import MagicMock, patch

import pytest
from cryptography.fernet import Fernet

from src.services.github_service import (
    create_repository,
    delete_repository,
    list_repositories,
)


@pytest.fixture(autouse=True)
def _setup_env(tmp_path, monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("MCP_ENCRYPTION_KEY", key)
    token_path = tmp_path / "token.enc"
    monkeypatch.setenv("MCP_TOKEN_PATH", str(token_path))

    from src.services.token_service import store_token

    store_token("ghp_fake_token")


def _mock_repo(**overrides):
    defaults = {
        "name": "test-repo",
        "full_name": "user/test-repo",
        "private": True,
        "html_url": "https://github.com/user/test-repo",
        "description": "A test repo",
        "language": "Python",
        "default_branch": "main",
    }
    defaults.update(overrides)
    repo = MagicMock()
    for attr, value in defaults.items():
        setattr(repo, attr, value)
    return repo


@patch("src.services.github_service.Github")
def test_list_repositories(mock_github_cls):
    mock_gh = MagicMock()
    mock_github_cls.return_value = mock_gh
    mock_gh.get_user.return_value.get_repos.return_value = [
        _mock_repo(name="repo-a"),
        _mock_repo(name="repo-b"),
    ]

    result = list_repositories()

    assert len(result) == 2
    assert result[0]["name"] == "repo-a"
    assert result[1]["name"] == "repo-b"
    mock_gh.close.assert_called_once()


@patch("src.services.github_service.Github")
def test_create_repository(mock_github_cls):
    mock_gh = MagicMock()
    mock_github_cls.return_value = mock_gh
    mock_gh.get_user.return_value.create_repo.return_value = _mock_repo(
        name="new-repo", description="My new repo"
    )

    result = create_repository(name="new-repo", description="My new repo", private=True)

    assert result["name"] == "new-repo"
    assert result["description"] == "My new repo"
    mock_gh.close.assert_called_once()


@patch("src.services.github_service.Github")
def test_delete_repository(mock_github_cls):
    mock_gh = MagicMock()
    mock_github_cls.return_value = mock_gh
    mock_repo = _mock_repo(name="old-repo", full_name="user/old-repo")
    mock_gh.get_user.return_value.get_repo.return_value = mock_repo

    result = delete_repository(name="old-repo")

    assert result["deleted"] is True
    assert result["full_name"] == "user/old-repo"
    mock_repo.delete.assert_called_once()
    mock_gh.close.assert_called_once()
