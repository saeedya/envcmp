"""Integration tests for diff between real providers."""

from pathlib import Path

import pytest

from envcmp.differ import diff
from envcmp.providers.env_file import EnvFileProvider

pytestmark = pytest.mark.integration


class TestDiffIntegration:
    def test_diff_between_two_env_files(self, tmp_path: Path):
        source = tmp_path / "source.env"
        target = tmp_path / "target.env"

        source.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPI_KEY=abc\n")
        target.write_text("DB_HOST=localhost\nDB_PORT=5432\n")

        source_provider = EnvFileProvider(str(source))
        target_provider = EnvFileProvider(str(target))

        result = diff(source_provider, target_provider)

        assert len(result.in_sync) == 2
        assert len(result.source_only) == 1
        assert result.source_only[0].key == "API_KEY"
        assert result.is_clean is False

    def test_diff_vault_and_env_file(self, vault_path: str, tmp_path: Path):
        env_file = tmp_path / "test.env"
        env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")

        from envcmp.providers.vault import VaultProvider

        vault_provider = VaultProvider(
            addr="http://localhost:8200",
            token="root",
            path=vault_path,
        )
        env_provider = EnvFileProvider(str(env_file))

        result = diff(vault_provider, env_provider)
        assert result is not None
