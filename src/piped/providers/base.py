"""Base provider interface for piped."""

from abc import ABC, abstractmethod
from piped.models import Variable


class BaseProvider(ABC):
    """Abstract base class that all providers must inherit from."""

    @abstractmethod
    def list(self) -> list[Variable]:
        """Fetch all variables from the provider."""
        ...

    @abstractmethod
    def write(self, variable: Variable) -> None:
        """Write a variable to the provider."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a variable from the provider by key."""
        ...