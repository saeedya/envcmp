"""Unit tests for Config loader."""

from envcmp.config import Config, GitHubConfig, GitLabConfig, TerraformCloudConfig, load


class TestConfig:
    def test_load_gitlab_config(self, monkeypatch):
        monkeypatch.setenv("GITLAB_URL", "https://gitlab.com")
        monkeypatch.setenv("GITLAB_TOKEN", "test-token")
        monkeypatch.setenv("GITLAB_PROJECT_ID", "123")
        config = load()
        assert config.gitlab == GitLabConfig(
            url="https://gitlab.com",
            token="test-token",
            project_id="123",
        )

    def test_load_github_config(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "test-token")
        monkeypatch.setenv("GITHUB_ORGANIZATION", "my-org")
        monkeypatch.setenv("GITHUB_REPOSITORY", "my-repo")
        config = load()
        assert config.github == GitHubConfig(
            token="test-token",
            organization="my-org",
            repository="my-repo",
        )

    def test_load_terraform_config(self, monkeypatch):
        monkeypatch.setenv("TERRAFORM_TOKEN", "test-token")
        monkeypatch.setenv("TERRAFORM_ORGANIZATION", "my-org")
        monkeypatch.setenv("TERRAFORM_WORKSPACE", "my-workspace")
        config = load()
        assert config.terraform == TerraformCloudConfig(
            token="test-token",
            organization="my-org",
            workspace="my-workspace",
        )

    def test_load_empty_config(self, monkeypatch):
        monkeypatch.delenv("GITLAB_URL", raising=False)
        monkeypatch.delenv("GITLAB_TOKEN", raising=False)
        monkeypatch.delenv("GITLAB_PROJECT_ID", raising=False)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_ORGANIZATION", raising=False)
        monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
        monkeypatch.delenv("TERRAFORM_TOKEN", raising=False)
        monkeypatch.delenv("TERRAFORM_ORGANIZATION", raising=False)
        monkeypatch.delenv("TERRAFORM_WORKSPACE", raising=False)
        config = load()
        assert config == Config()
        assert config.gitlab is None
        assert config.github is None
        assert config.terraform is None
