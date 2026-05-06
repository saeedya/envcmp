"""Integration tests for VaultProvider — requires running Vault instance."""

import pytest

from envcmp.models import Variable
from envcmp.providers.vault import VaultProvider

pytestmark = pytest.mark.integration


class TestVaultProviderIntegration:
    def test_list_returns_variables(self, vault_path: str):
        provider = VaultProvider(
            addr="http://localhost:8200",
            token="root",
            path=vault_path,
        )
        variables = provider.list()
        assert len(variables) == 2
        keys = [v.key for v in variables]
        assert "DB_HOST" in keys
        assert "DB_PORT" in keys

    def test_all_variables_marked_as_secret(self, vault_path: str):
        provider = VaultProvider(
            addr="http://localhost:8200",
            token="root",
            path=vault_path,
        )
        variables = provider.list()
        assert all(v.is_secret for v in variables)

    def test_write_adds_new_variable(self, vault_path: str):
        provider = VaultProvider(
            addr="http://localhost:8200",
            token="root",
            path=vault_path,
        )
        provider.write(Variable("NEW_KEY", "new_value"))
        variables = provider.list()
        keys = [v.key for v in variables]
        assert "NEW_KEY" in keys

    def test_write_updates_existing_variable(self, vault_path: str):
        provider = VaultProvider(
            addr="http://localhost:8200",
            token="root",
            path=vault_path,
        )
        provider.write(Variable("DB_HOST", "remotehost"))
        variables = provider.list()
        db_host = next(v for v in variables if v.key == "DB_HOST")
        assert db_host.value == "remotehost"

    def test_delete_removes_variable(self, vault_path: str):
        provider = VaultProvider(
            addr="http://localhost:8200",
            token="root",
            path=vault_path,
        )
        provider.delete("DB_HOST")
        variables = provider.list()
        keys = [v.key for v in variables]
        assert "DB_HOST" not in keys
