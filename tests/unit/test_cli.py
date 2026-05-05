"""Unit tests for cli.py"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from piped.cli import app

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
        result = runner.invoke(app, [
            "--source", str(source_env),
            "--target", str(target_env),
        ])
        assert result.exit_code == 0
        assert "in sync" in result.output

    def test_differs(self, source_env: Path, target_env: Path):
        target_env.write_text("DB_HOST=remotehost\nDB_PORT=5432\n")
        result = runner.invoke(app, [
            "--source", str(source_env),
            "--target", str(target_env),
        ])
        assert result.exit_code == 1
        assert "differs" in result.output

    def test_source_only(self, source_env: Path, target_env: Path):
        target_env.write_text("DB_HOST=localhost\n")
        result = runner.invoke(app, [
            "--source", str(source_env),
            "--target", str(target_env),
        ])
        assert result.exit_code == 1
        assert "source only" in result.output

    def test_target_only(self, source_env: Path, target_env: Path):
        target_env.write_text("DB_HOST=localhost\nDB_PORT=5432\nEXTRA=extra\n")
        result = runner.invoke(app, [
            "--source", str(source_env),
            "--target", str(target_env),
        ])
        assert result.exit_code == 1
        assert "target only" in result.output