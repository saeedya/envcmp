"""Unit tests for VaultProvider."""

import pytest
from pytest_mock import MockerFixture

from envcmp.models import Variable
from envcmp.providers.vault import VaultProvider


@pytest.fixture
def provider() -> VaultProvider:
    return VaultProvider(
        addr="http://localhost:8200",
        token="root",
        path="secret/data/my-app",
    )


@pytest.fixture
def mock_vault_response() -> dict:
    return {
        "data": {
            "data": {
                "DB_HOST": "localhost",
                "DB_PASS": "secret123",
            }
        }
    }


class TestVaultProvider:
    def test_parse_path(self, provider: VaultProvider):
        mount, secret_path = provider._parse_path()
        assert mount == "secret"
        assert secret_path == "my-app"

    def test_list_returns_variables(
        self,
        provider: VaultProvider,
        mock_vault_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            provider._client.secrets.kv.v2,
            "read_secret_version",
            return_value=mock_vault_response,
        )
        variables = provider.list()
        assert len(variables) == 2
        assert Variable("DB_HOST", "localhost", True) in variables

    def test_list_marks_all_as_secret(
        self,
        provider: VaultProvider,
        mock_vault_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            provider._client.secrets.kv.v2,
            "read_secret_version",
            return_value=mock_vault_response,
        )
        variables = provider.list()
        assert all(v.is_secret for v in variables)

    def test_write_creates_new_secret(
        self,
        provider: VaultProvider,
        mock_vault_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            provider._client.secrets.kv.v2,
            "read_secret_version",
            return_value=mock_vault_response,
        )
        mock_create = mocker.patch.object(
            provider._client.secrets.kv.v2,
            "create_or_update_secret",
        )
        provider.write(Variable("NEW_KEY", "new_value"))
        assert mock_create.called

    def test_write_updates_existing_secret(
        self,
        provider: VaultProvider,
        mock_vault_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            provider._client.secrets.kv.v2,
            "read_secret_version",
            return_value=mock_vault_response,
        )
        mock_create = mocker.patch.object(
            provider._client.secrets.kv.v2,
            "create_or_update_secret",
        )
        provider.write(Variable("DB_HOST", "newhost"))
        assert mock_create.called
        call_args = mock_create.call_args
        assert call_args.kwargs["secret"]["DB_HOST"] == "newhost"

    def test_delete_removes_key(
        self,
        provider: VaultProvider,
        mock_vault_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            provider._client.secrets.kv.v2,
            "read_secret_version",
            return_value=mock_vault_response,
        )
        mock_create = mocker.patch.object(
            provider._client.secrets.kv.v2,
            "create_or_update_secret",
        )
        provider.delete("DB_HOST")
        assert mock_create.called
        call_args = mock_create.call_args
        assert "DB_HOST" not in call_args.kwargs["secret"]

    def test_delete_nonexistent_key_does_nothing(
        self,
        provider: VaultProvider,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            provider._client.secrets.kv.v2,
            "read_secret_version",
            side_effect=Exception("not found"),
        )
        provider.delete("MISSING_KEY")  # should not raise

    def test_write_creates_secret_when_path_not_exists(
        self,
        provider: VaultProvider,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            provider._client.secrets.kv.v2,
            "read_secret_version",
            side_effect=Exception("path not found"),
        )
        mock_create = mocker.patch.object(
            provider._client.secrets.kv.v2,
            "create_or_update_secret",
        )
        provider.write(Variable("NEW_KEY", "new_value"))
        assert mock_create.called
        call_args = mock_create.call_args
        assert call_args.kwargs["secret"]["NEW_KEY"] == "new_value"
