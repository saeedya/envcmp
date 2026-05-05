"""Unit tests for GitHubProvider."""

import base64

import pytest
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from pytest_mock import MockerFixture

from envcmp.models import Variable
from envcmp.providers.github import GitHubProvider


@pytest.fixture
def provider() -> GitHubProvider:
    return GitHubProvider(
        token="test-token",
        organization="my-org",
        repository="my-repo",
    )


@pytest.fixture
def mock_secrets_response() -> dict:
    return {
        "secrets": [
            {"name": "API_KEY"},
            {"name": "DB_HOST"},
        ]
    }


class TestGitHubProvider:
    def test_list_returns_variables(
        self, provider: GitHubProvider, mock_secrets_response: dict, mocker: MockerFixture
    ):
        mocker.patch("envcmp.providers.github.httpx.get").return_value = mocker.Mock(
            json=lambda: mock_secrets_response,
            raise_for_status=lambda: None,
        )
        variables = provider.list()
        assert len(variables) == 2
        assert Variable("API_KEY", None, True) in variables
        assert Variable("DB_HOST", None, True) in variables

    def test_write_creates_secret(self, provider: GitHubProvider, mocker: MockerFixture):
        mocker.patch("envcmp.providers.github.httpx.get").return_value = mocker.Mock(
            json=lambda: {"key": "abc123", "key_id": "123"},
            raise_for_status=lambda: None,
        )
        mocker.patch.object(provider, "_encrypt", return_value="encrypted-value")
        mock_put = mocker.patch("envcmp.providers.github.httpx.put")
        mock_put.return_value = mocker.Mock(raise_for_status=lambda: None)
        provider.write(Variable("NEW_SECRET", "new-value", True))
        assert mock_put.called

    def test_delete_secret(self, provider: GitHubProvider, mocker: MockerFixture):
        mock_delete = mocker.patch("envcmp.providers.github.httpx.delete")
        mock_delete.return_value = mocker.Mock(raise_for_status=lambda: None)
        provider.delete("DB_HOST")
        assert mock_delete.called

    def test_encrypt_returns_string(self, provider: GitHubProvider):
        private_key = X25519PrivateKey.generate()
        public_key = private_key.public_key()
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        public_bytes = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        public_key_b64 = base64.b64encode(public_bytes).decode()

        result = provider._encrypt("my-secret", public_key_b64)
        assert isinstance(result, str)
        assert len(result) > 0
