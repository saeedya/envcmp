"""Terraform Cloud Variables provider for piped."""

import httpx

from piped.models import Variable
from piped.providers.base import BaseProvider


class TerraformProvider(BaseProvider):
    """Reads and writes Terraform Cloud workspace variables via the API."""

    BASE_URL = "https://app.terraform.io/api/v2"

    def __init__(self, token: str, organization: str, workspace: str) -> None:
        self._token = token
        self._organization = organization
        self._workspace = workspace
        self._workspace_id_cache: str | None = None
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
        }

    def _workspace_id(self) -> str:
        """Fetch and cache the workspace ID from Terraform Cloud."""
        if self._workspace_id_cache is not None:
            return self._workspace_id_cache
        url = f"{self.BASE_URL}/organizations/{self._organization}/workspaces/{self._workspace}"
        response = httpx.get(url, headers=self._headers)
        response.raise_for_status()
        self._workspace_id_cache = response.json()["data"]["id"]
        return self._workspace_id_cache

    def _vars_url(self) -> str:
        """Build the variables API URL for the workspace."""
        return f"{self.BASE_URL}/workspaces/{self._workspace_id()}/vars"

    def list(self) -> list[Variable]:
        """Fetch all variables from the Terraform Cloud workspace."""
        response = httpx.get(self._vars_url(), headers=self._headers)
        response.raise_for_status()
        return [
            Variable(
                key=var["attributes"]["key"],
                value=var["attributes"]["value"],
                is_secret=var["attributes"].get("sensitive", False),
            )
            for var in response.json()["data"]
        ]

    def write(self, variable: Variable) -> None:
        """Create or update a variable in the Terraform Cloud workspace."""
        vars_url = self._vars_url()
        existing = {v.key: v for v in self.list()}

        payload = {
            "data": {
                "type": "vars",
                "attributes": {
                    "key": variable.key,
                    "value": variable.value,
                    "category": "env",
                },
            }
        }

        if variable.key in existing:
            response = httpx.patch(
                f"{vars_url}/{variable.key}",
                headers=self._headers,
                json=payload,
            )
        else:
            response = httpx.post(
                vars_url,
                headers=self._headers,
                json=payload,
            )
        response.raise_for_status()

    def delete(self, key: str) -> None:
        """Delete a variable from the Terraform Cloud workspace."""
        response = httpx.delete(
            f"{self._vars_url()}/{key}",
            headers=self._headers,
        )
        response.raise_for_status()
