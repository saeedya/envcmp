"""Unit tests for EnvFileProvider."""

import pytest
from pathlib import Path
from piped.models import Variable
from piped.providers.env_file import EnvFileProvider


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    """Create a temporary .env file for testing."""
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    return f


class TestEnvFileProvider:
    def test_list_returns_variables(self, env_file: Path):
        provider = EnvFileProvider(str(env_file))
        variables = provider.list()
        assert len(variables) == 2
        assert Variable("DB_HOST", "localhost") in variables
        assert Variable("DB_PORT", "5432") in variables

    def test_list_skips_comments(self, tmp_path: Path):
        f = tmp_path / ".env"
        f.write_text("# this is a comment\nKEY=value\n")
        provider = EnvFileProvider(str(f))
        assert len(provider.list()) == 1

    def test_list_skips_empty_lines(self, tmp_path: Path):
        f = tmp_path / ".env"
        f.write_text("\n\nKEY=value\n\n")
        provider = EnvFileProvider(str(f))
        assert len(provider.list()) == 1

    def test_list_returns_empty_when_file_not_exists(self, tmp_path: Path):
        provider = EnvFileProvider(str(tmp_path / "missing.env"))
        assert provider.list() == []

    def test_write_adds_new_variable(self, env_file: Path):
        provider = EnvFileProvider(str(env_file))
        provider.write(Variable("NEW_KEY", "new_value"))
        assert Variable("NEW_KEY", "new_value") in provider.list()

    def test_write_updates_existing_variable(self, env_file: Path):
        provider = EnvFileProvider(str(env_file))
        provider.write(Variable("DB_HOST", "remotehost"))
        variables = provider.list()
        assert Variable("DB_HOST", "remotehost") in variables
        assert Variable("DB_HOST", "localhost") not in variables

    def test_delete_removes_variable(self, env_file: Path):
        provider = EnvFileProvider(str(env_file))
        provider.delete("DB_HOST")
        assert Variable("DB_HOST", "localhost") not in provider.list()

    def test_delete_on_missing_file_does_nothing(self, tmp_path: Path):
        provider = EnvFileProvider(str(tmp_path / "missing.env"))
        provider.delete("KEY")  # should not raise

    def test_list_skips_lines_without_equals(self, tmp_path: Path):
        f = tmp_path / ".env"
        f.write_text("INVALID_LINE\nKEY=value\n")
        provider = EnvFileProvider(str(f))
        assert len(provider.list()) == 1

    def test_write_creates_file_if_not_exists(self, tmp_path: Path):
        f = tmp_path / ".env"
        provider = EnvFileProvider(str(f))
        provider.write(Variable("KEY", "value"))
        assert Variable("KEY", "value") in provider.list()