"""Integration test configuration and fixtures."""

import hvac
import pytest


@pytest.fixture(scope="session")
def vault_client():
    """Create a real Vault client for integration tests."""
    client = hvac.Client(url="http://localhost:8200", token="root")
    if not client.is_authenticated():
        pytest.skip(
            "Vault is not running — start with: \
                docker-compose -f docker-compose.test.yml up -d"
        )
    return client


@pytest.fixture(scope="function")
def vault_path(vault_client):
    """Create a test path in Vault and clean up after."""
    path = "test-app"
    mount = "secret"

    # setup
    vault_client.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret={"DB_HOST": "localhost", "DB_PORT": "5432"},
        mount_point=mount,
    )

    yield f"{mount}/data/{path}"

    # teardown
    try:
        vault_client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=path,
            mount_point=mount,
        )
    except Exception:
        pass
