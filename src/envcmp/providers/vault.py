"""HashiCorp Vault provider for envcmp."""

import hvac

from envcmp.models import Variable
from envcmp.providers.base import BaseProvider


class VaultProvider(BaseProvider):
    """Reads and writes secrets from HashiCorp Vault KV v2."""

    def __init__(self, addr: str, token: str, path: str) -> None:
        self._path = path
        self._client = hvac.Client(url=addr, token=token)

    def _parse_path(self) -> tuple[str, str]:
        """Split path into mount point and secret path.

        Example: 'secret/data/my-app' → ('secret', 'my-app')
        """
        parts = self._path.split("/")
        mount = parts[0]
        secret_path = "/".join(parts[2:]) if len(parts) > 2 else parts[-1]
        return mount, secret_path

    def list(self) -> list[Variable]:
        """Fetch all secrets from Vault KV v2."""
        mount, secret_path = self._parse_path()
        response = self._client.secrets.kv.v2.read_secret_version(
            path=secret_path,
            mount_point=mount,
        )
        data = response["data"]["data"]
        return [Variable(key=key, value=str(value), is_secret=True) for key, value in data.items()]

    def write(self, variable: Variable) -> None:
        """Write a secret to Vault KV v2."""
        mount, secret_path = self._parse_path()
        try:
            existing = self._client.secrets.kv.v2.read_secret_version(
                path=secret_path,
                mount_point=mount,
            )
            data = existing["data"]["data"]
        except Exception:
            data = {}

        data[variable.key] = variable.value
        self._client.secrets.kv.v2.create_or_update_secret(
            path=secret_path,
            secret=data,
            mount_point=mount,
        )

    def delete(self, key: str) -> None:
        """Delete a secret key from Vault KV v2."""
        mount, secret_path = self._parse_path()
        try:
            existing = self._client.secrets.kv.v2.read_secret_version(
                path=secret_path,
                mount_point=mount,
            )
            data = existing["data"]["data"]
        except Exception:
            return

        data.pop(key, None)
        self._client.secrets.kv.v2.create_or_update_secret(
            path=secret_path,
            secret=data,
            mount_point=mount,
        )
