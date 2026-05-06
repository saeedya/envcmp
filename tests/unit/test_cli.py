"""Unit tests for cli.py"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from envcmp.cli import app
from envcmp.models import Variable
from envcmp.providers.env_file import EnvFileProvider

runner = CliRunner()


@pytest.fixture
def source_env(tmp_path: Path) -> Path:
    f = tmp_path / "source.env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    return f


@pytest.fixture
def target_env(tmp_path: Path) -> Path:
    f = tmp_path / "target.env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    return f


class TestDiffCommand:
    def test_in_sync(self, source_env: Path, target_env: Path):
        result = runner.invoke(
            app,
            [
                "diff",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
            ],
        )
        assert result.exit_code == 0
        assert "in sync" in result.output

    def test_differs(self, source_env: Path, target_env: Path):
        target_env.write_text("DB_HOST=remotehost\nDB_PORT=5432\n")
        result = runner.invoke(
            app,
            [
                "diff",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
            ],
        )
        assert result.exit_code == 1
        assert "differs" in result.output

    def test_source_only(self, source_env: Path, target_env: Path):
        target_env.write_text("DB_HOST=localhost\n")
        result = runner.invoke(
            app,
            [
                "diff",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
            ],
        )
        assert result.exit_code == 1
        assert "source only" in result.output

    def test_target_only(self, source_env: Path, target_env: Path):
        target_env.write_text("DB_HOST=localhost\nDB_PORT=5432\nEXTRA=extra\n")
        result = runner.invoke(
            app,
            [
                "diff",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
            ],
        )
        assert result.exit_code == 1
        assert "target only" in result.output


class TestResolveProvider:
    def test_resolve_env_provider(self, source_env: Path):
        from envcmp.cli import resolve_provider
        from envcmp.providers.env_file import EnvFileProvider

        provider = resolve_provider(f"env:{source_env}")
        assert isinstance(provider, EnvFileProvider)

    def test_resolve_invalid_format(self):
        from envcmp.cli import resolve_provider

        with pytest.raises(ValueError, match="Invalid provider format"):
            resolve_provider("invalid")

    def test_resolve_unsupported_kind(self):
        from envcmp.cli import resolve_provider

        with pytest.raises(ValueError, match="Unsupported provider"):
            resolve_provider("unknown:something")

    def test_resolve_gitlab_without_config(self, monkeypatch):
        from envcmp.cli import resolve_provider

        monkeypatch.delenv("GITLAB_TOKEN", raising=False)
        monkeypatch.delenv("GITLAB_URL", raising=False)
        monkeypatch.delenv("GITLAB_PROJECT_ID", raising=False)
        with pytest.raises(ValueError, match="GitLab is not configured"):
            resolve_provider("gitlab:my-project")

    def test_resolve_github_without_config(self, monkeypatch):
        from envcmp.cli import resolve_provider

        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_ORGANIZATION", raising=False)
        monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
        with pytest.raises(ValueError, match="GitHub is not configured"):
            resolve_provider("github:my-repo")

    def test_resolve_terraform_without_config(self, monkeypatch):
        from envcmp.cli import resolve_provider

        monkeypatch.delenv("TERRAFORM_TOKEN", raising=False)
        monkeypatch.delenv("TERRAFORM_ORGANIZATION", raising=False)
        monkeypatch.delenv("TERRAFORM_WORKSPACE", raising=False)
        with pytest.raises(ValueError, match="Terraform is not configured"):
            resolve_provider("terraform:my-workspace")

    def test_resolve_gitlab_with_config(self, monkeypatch):
        from envcmp.cli import resolve_provider
        from envcmp.providers.gitlab import GitLabProvider

        monkeypatch.setenv("GITLAB_URL", "https://gitlab.com")
        monkeypatch.setenv("GITLAB_TOKEN", "test-token")
        monkeypatch.setenv("GITLAB_PROJECT_ID", "123")
        provider = resolve_provider("gitlab:my-project")
        assert isinstance(provider, GitLabProvider)

    def test_resolve_github_with_config(self, monkeypatch):
        from envcmp.cli import resolve_provider
        from envcmp.providers.github import GitHubProvider

        monkeypatch.setenv("GITHUB_TOKEN", "test-token")
        monkeypatch.setenv("GITHUB_ORGANIZATION", "my-org")
        monkeypatch.setenv("GITHUB_REPOSITORY", "my-repo")
        provider = resolve_provider("github:my-repo")
        assert isinstance(provider, GitHubProvider)

    def test_resolve_terraform_with_config(self, monkeypatch):
        from envcmp.cli import resolve_provider
        from envcmp.providers.terraform import TerraformProvider

        monkeypatch.setenv("TERRAFORM_TOKEN", "test-token")
        monkeypatch.setenv("TERRAFORM_ORGANIZATION", "my-org")
        monkeypatch.setenv("TERRAFORM_WORKSPACE", "my-workspace")
        provider = resolve_provider("terraform:my-workspace")
        assert isinstance(provider, TerraformProvider)

    def test_resolve_vault_without_config(self, monkeypatch):
        from envcmp.cli import resolve_provider

        monkeypatch.delenv("VAULT_ADDR", raising=False)
        monkeypatch.delenv("VAULT_TOKEN", raising=False)
        monkeypatch.delenv("VAULT_PATH", raising=False)
        with pytest.raises(ValueError, match="Vault is not configured"):
            resolve_provider("vault:secret/data/my-app")

    def test_resolve_vault_with_config(self, monkeypatch):
        from envcmp.cli import resolve_provider
        from envcmp.providers.vault import VaultProvider

        monkeypatch.setenv("VAULT_ADDR", "http://localhost:8200")
        monkeypatch.setenv("VAULT_TOKEN", "root")
        monkeypatch.setenv("VAULT_PATH", "secret/data/my-app")
        provider = resolve_provider("vault:secret/data/my-app")
        assert isinstance(provider, VaultProvider)


class TestPushCommand:
    def test_push_in_sync(self, source_env: Path, target_env: Path):
        result = runner.invoke(
            app,
            [
                "push",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
            ],
        )
        assert result.exit_code == 0
        assert "in sync" in result.output

    def test_push_dry_run(self, source_env: Path, target_env: Path):
        target_env.write_text("")
        result = runner.invoke(
            app,
            [
                "push",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "DB_HOST" in result.output

    def test_push_applies_changes(self, source_env: Path, target_env: Path):
        target_env.write_text("")
        result = runner.invoke(
            app,
            [
                "push",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
            ],
        )
        assert result.exit_code == 0
        assert "pushed" in result.output
        provider = EnvFileProvider(str(target_env))
        variables = provider.list()
        assert Variable("DB_HOST", "localhost") in variables
        assert Variable("DB_PORT", "5432") in variables


class TestPullCommand:
    def test_pull_in_sync(self, source_env: Path, target_env: Path):
        result = runner.invoke(
            app,
            [
                "pull",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
            ],
        )
        assert result.exit_code == 0
        assert "in sync" in result.output

    def test_pull_dry_run(self, source_env: Path, target_env: Path):
        source_env.write_text("")
        result = runner.invoke(
            app,
            [
                "pull",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "DB_HOST" in result.output

    def test_pull_applies_changes(self, source_env: Path, target_env: Path):
        source_env.write_text("")
        result = runner.invoke(
            app,
            [
                "pull",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
            ],
        )
        assert result.exit_code == 0
        assert "pulled" in result.output
        provider = EnvFileProvider(str(source_env))
        variables = provider.list()
        assert Variable("DB_HOST", "localhost") in variables
        assert Variable("DB_PORT", "5432") in variables


class TestFilterFlag:
    def test_diff_with_filter(self, source_env: Path, target_env: Path):
        target_env.write_text("DB_HOST=localhost\n")
        result = runner.invoke(
            app,
            [
                "diff",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
                "--filter",
                "DB_*",
            ],
        )
        assert "DB_HOST" in result.output
        assert "DB_PORT" in result.output

    def test_push_with_filter(self, source_env: Path, target_env: Path):
        target_env.write_text("")
        result = runner.invoke(
            app,
            [
                "push",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
                "--filter",
                "DB_HOST",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "DB_HOST" in result.output

    def test_pull_with_filter(self, source_env: Path, target_env: Path):
        source_env.write_text("")
        result = runner.invoke(
            app,
            [
                "pull",
                "--from",
                f"env:{source_env}",
                "--to",
                f"env:{target_env}",
                "--filter",
                "DB_HOST",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "DB_HOST" in result.output
