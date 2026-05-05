"""Unit tests for TerraformProvider."""

import pytest
from pytest_mock import MockerFixture
from piped.models import Variable
from piped.providers.terraform import TerraformProvider


@pytest.fixture
def provider() -> TerraformProvider:
    return TerraformProvider(
        token="test-token",
        organization="my-org",
        workspace="my-workspace",
    )


@pytest.fixture
def mock_workspace_response() -> dict:
    return {"data": {"id": "ws-123"}}


@pytest.fixture
def mock_variables_response() -> dict:
    return {
        "data": [
            {
                "id": "var-1",
                "attributes": {"key": "DB_HOST", "value": "localhost", "sensitive": False},
            },
            {
                "id": "var-2",
                "attributes": {"key": "DB_PASS", "value": "secret", "sensitive": True},
            },
        ]
    }


class TestTerraformProvider:
    def test_list_returns_variables(
        self,
        provider: TerraformProvider,
        mock_workspace_response: dict,
        mock_variables_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch("piped.providers.terraform.httpx.get").side_effect = [
            mocker.Mock(json=lambda: mock_workspace_response, raise_for_status=lambda: None),
            mocker.Mock(json=lambda: mock_variables_response, raise_for_status=lambda: None),
        ]
        variables = provider.list()
        assert len(variables) == 2
        assert Variable("DB_HOST", "localhost") in variables

    def test_list_marks_sensitive_as_secret(
        self,
        provider: TerraformProvider,
        mock_workspace_response: dict,
        mock_variables_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch("piped.providers.terraform.httpx.get").side_effect = [
            mocker.Mock(json=lambda: mock_workspace_response, raise_for_status=lambda: None),
            mocker.Mock(json=lambda: mock_variables_response, raise_for_status=lambda: None),
        ]
        variables = provider.list()
        db_pass = next(v for v in variables if v.key == "DB_PASS")
        assert db_pass.is_secret is True

    def test_write_creates_new_variable(
        self,
        provider: TerraformProvider,
        mock_workspace_response: dict,
        mock_variables_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch("piped.providers.terraform.httpx.get").side_effect = [
            mocker.Mock(json=lambda: mock_workspace_response, raise_for_status=lambda: None),
            mocker.Mock(json=lambda: {"data": []}, raise_for_status=lambda: None),
        ]
        mock_post = mocker.patch("piped.providers.terraform.httpx.post")
        mock_post.return_value = mocker.Mock(raise_for_status=lambda: None)
        provider.write(Variable("NEW_KEY", "new_value"))
        assert mock_post.called

    def test_write_updates_existing_variable(
        self,
        provider: TerraformProvider,
        mock_workspace_response: dict,
        mock_variables_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch("piped.providers.terraform.httpx.get").side_effect = [
            mocker.Mock(json=lambda: mock_workspace_response, raise_for_status=lambda: None),
            mocker.Mock(json=lambda: mock_variables_response, raise_for_status=lambda: None),
        ]
        mock_patch = mocker.patch("piped.providers.terraform.httpx.patch")
        mock_patch.return_value = mocker.Mock(raise_for_status=lambda: None)
        provider.write(Variable("DB_HOST", "newhost"))
        assert mock_patch.called

    def test_delete_variable(
        self,
        provider: TerraformProvider,
        mock_workspace_response: dict,
        mocker: MockerFixture,
    ):
        mocker.patch("piped.providers.terraform.httpx.get").return_value = mocker.Mock(
            json=lambda: mock_workspace_response, raise_for_status=lambda: None
        )
        mock_delete = mocker.patch("piped.providers.terraform.httpx.delete")
        mock_delete.return_value = mocker.Mock(raise_for_status=lambda: None)
        provider.delete("DB_HOST")
        assert mock_delete.called