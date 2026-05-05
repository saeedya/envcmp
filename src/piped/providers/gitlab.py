"""GitLab CI Variables provider for piped."""

import httpx

from piped.models import Variable
from piped.providers.base import BaseProvider


class GitLabProvider(BaseProvider):
    """Reads and writes GitLab CI/CD variables via the GitLab API."""

    def __init__(self, url: str, token: str, project_id: str) -> None:
        self._url = url.rstrip("/")
        self._token = token
        self._project_id = project_id
        self._headers = {"PRIVATE-TOKEN": token}

    def _api_url(self) -> str:
        """Build the GitLab API URL for project variables."""
        return f"{self._url}/api/v4/projects/{self._project_id}/variables"

    def list(self) -> list[Variable]:
        """Fetch all CI/CD variables from GitLab project."""
        response = httpx.get(self._api_url(), headers=self._headers)
        response.raise_for_status()
        return [
            Variable(
                key=var["key"],
                value=var["value"],
                is_secret=var.get("masked", False),
            )
            for var in response.json()
        ]

    def write(self, variable: Variable) -> None:
        """Create or update a CI/CD variable in GitLab."""
        existing_keys = {v.key for v in self.list()}

        if variable.key in existing_keys:
            response = httpx.put(
                f"{self._api_url()}/{variable.key}",
                headers=self._headers,
                json={"value": variable.value},
            )
        else:
            response = httpx.post(
                self._api_url(),
                headers=self._headers,
                json={"key": variable.key, "value": variable.value},
            )
        response.raise_for_status()

    def delete(self, key: str) -> None:
        """Delete a CI/CD variable from GitLab."""
        response = httpx.delete(
            f"{self._api_url()}/{key}",
            headers=self._headers,
        )
        response.raise_for_status()
