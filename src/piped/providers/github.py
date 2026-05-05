"""GitHub Actions Secrets provider for piped."""

import base64

import httpx
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from piped.models import Variable
from piped.providers.base import BaseProvider

class GitHubProvider(BaseProvider):
    """Reads and writes GitHub Actions Secrets via the API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, organization: str, repository: str) -> None:
        self._token = token
        self._organization = organization
        self._repository = repository
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        }

    def _secrets_url(self) -> str:
        """Build the GitHub API URL for repository secrets."""
        return f"{self.BASE_URL}/repos/{self._organization}/{self._repository}/actions/secrets"
    
    def list(self) -> list[Variable]:
        """Fetch all secrets from the GitHub repository."""
        response = httpx.get(self._secrets_url(), headers=self._headers)
        response.raise_for_status()
        return [
            Variable(key=secret["name"], value=None, is_secret=True)
            for secret in response.json().get("secrets", [])
        ]
    
    def write(self, variable: Variable) -> None:
        """Create or update a secret in the GitHub repository."""
        # GitHub requires secrets to be encrypted with the repository's public key
        public_key_response = httpx.get(f"{self._secrets_url()}/public-key", headers=self._headers)
        public_key_response.raise_for_status()
        public_key = public_key_response.json()
        
        # Encrypt the secret value using the public key (encryption logic not shown here)
        encrypted_value = self._encrypt(variable.value or "", public_key["key"])
        
        payload = {
            "encrypted_value": encrypted_value,
            "key_id": public_key["key_id"],
        }
        
        response = httpx.put(
            f"{self._secrets_url()}/{variable.key}",
            headers=self._headers,
            json=payload,
        )
        response.raise_for_status()

    def delete(self, key: str) -> None:
        """Delete a secret from the GitHub repository."""
        response = httpx.delete(
            f"{self._secrets_url()}/{key}",
            headers=self._headers,
        )
        response.raise_for_status()

    def _encrypt(self, value: str, public_key: str) -> str:
        """Encrypt a secret value using the repo public key."""

        public_key_bytes = base64.b64decode(public_key)
        key = X25519PublicKey.from_public_bytes(public_key_bytes)
        public_bytes = key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        encrypted = bytes(a ^ b for a, b in zip(value.encode(), public_bytes))
        return base64.b64encode(encrypted).decode()
        