"""Environment file provider for piped."""

from pathlib import Path

from piped.models import Variable
from piped.providers.base import BaseProvider


class EnvFileProvider(BaseProvider):
    """Reads and writes variables from a .env file."""

    def __init__(self, path: str) -> None:
        self._path = Path(path)

    def list(self) -> list[Variable]:
        """Read all variables from the .env file."""
        if not self._path.exists():
            return []

        variables = []
        for line in self._path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            variables.append(Variable(key=key.strip(), value=value.strip()))
        return variables

    def write(self, variable: Variable) -> None:
        """Write or update a variable in the .env file."""
        lines = []
        if self._path.exists():
            lines = self._path.read_text().splitlines()

        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f"{variable.key}="):
                lines[i] = f"{variable.key}={variable.value}"
                updated = True
                break

        if not updated:
            lines.append(f"{variable.key}={variable.value}")

        self._path.write_text("\n".join(lines) + "\n")

    def delete(self, key: str) -> None:
        """Delete a variable from the .env file."""
        if not self._path.exists():
            return

        lines = self._path.read_text().splitlines()
        lines = [line for line in lines if not line.startswith(f"{key}=")]
        self._path.write_text("\n".join(lines) + "\n")
