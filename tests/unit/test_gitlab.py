"""Unit tests for GitLabProvider."""

import pytest
from pytest_mock import MockerFixture

from piped.models import Variable
from piped.providers.gitlab import GitLabProvider


@pytest.fixture
def provider() -> GitLabProvider:
    return GitLabProvider(
        url="https://gitlab.com",
        token="test-token",
        project_id="123",
    )


@pytest.fixture
def mock_variables() -> list[dict]:
    return [
        {"key": "DB_HOST", "value": "localhost", "masked": False},
        {"key": "DB_PASS", "value": "secret", "masked": True},
    ]


class TestGitLabProvider:
    def test_list_returns_variables(
        self, provider: GitLabProvider, mock_variables: list[dict], mocker: MockerFixture
    ):
        mocker.patch("piped.providers.gitlab.httpx.get").return_value = mocker.Mock(
            json=lambda: mock_variables,
            raise_for_status=lambda: None,
        )
        variables = provider.list()
        assert len(variables) == 2
        assert Variable("DB_HOST", "localhost") in variables

    def test_list_marks_masked_as_secret(
        self, provider: GitLabProvider, mock_variables: list[dict], mocker: MockerFixture
    ):
        mocker.patch("piped.providers.gitlab.httpx.get").return_value = mocker.Mock(
            json=lambda: mock_variables,
            raise_for_status=lambda: None,
        )
        variables = provider.list()
        db_pass = next(v for v in variables if v.key == "DB_PASS")
        assert db_pass.is_secret is True

    def test_write_creates_new_variable(self, provider: GitLabProvider, mocker: MockerFixture):
        mocker.patch("piped.providers.gitlab.httpx.get").return_value = mocker.Mock(
            json=lambda: [],
            raise_for_status=lambda: None,
        )
        mock_post = mocker.patch("piped.providers.gitlab.httpx.post")
        mock_post.return_value = mocker.Mock(raise_for_status=lambda: None)
        provider.write(Variable("NEW_KEY", "new_value"))
        assert mock_post.called

    def test_write_updates_existing_variable(
        self, provider: GitLabProvider, mock_variables: list[dict], mocker: MockerFixture
    ):
        mocker.patch("piped.providers.gitlab.httpx.get").return_value = mocker.Mock(
            json=lambda: mock_variables,
            raise_for_status=lambda: None,
        )
        mock_put = mocker.patch("piped.providers.gitlab.httpx.put")
        mock_put.return_value = mocker.Mock(raise_for_status=lambda: None)
        provider.write(Variable("DB_HOST", "newhost"))
        assert mock_put.called

    def test_delete_variable(self, provider: GitLabProvider, mocker: MockerFixture):
        mock_delete = mocker.patch("piped.providers.gitlab.httpx.delete")
        mock_delete.return_value = mocker.Mock(raise_for_status=lambda: None)
        provider.delete("DB_HOST")
        assert mock_delete.called

    def test_api_url_format(self, provider: GitLabProvider):
        assert provider._api_url() == "https://gitlab.com/api/v4/projects/123/variables"
