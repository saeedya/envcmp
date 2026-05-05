"""Core data models for envcmp."""

from dataclasses import dataclass, field
from enum import StrEnum


class ProviderKind(StrEnum):
    """Supported provider types."""

    GITLAB = "gitlab"
    GITHUB = "github"
    TERRAFORM = "terraform"
    ENV_FILE = "env"


@dataclass
class Variable:
    """A CI/CD variable with a key and value.

    Value can be None — meaning it does not exist in this provider.
    """

    key: str
    value: str | None = None
    is_secret: bool = False  # should the value be masked in output?

    def __repr__(self) -> str:
        return f"Variable(key={self.key!r}, value={self.masked_value()!r})"

    def masked_value(self) -> str:
        """Return a safe representation of the value for display."""
        if self.value is None:
            return "(not set)"
        if self.is_secret:
            return "••••••••"
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Variable):
            return NotImplemented
        return self.key == other.key and self.value == other.value


@dataclass
class DiffResult:
    """Result of comparing variables between two providers.

    Each variable falls into one of four states:
    - in_sync: exists in both, values match
    - source_only: exists only in source
    - target_only: exists only in target
    - differs: exists in both but values differ
    """

    in_sync: list[Variable] = field(default_factory=list)
    source_only: list[Variable] = field(default_factory=list)
    target_only: list[Variable] = field(default_factory=list)
    differs: list[tuple[Variable, Variable]] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        """Return True if there are no differences."""
        return len(self.source_only) == 0 and len(self.target_only) == 0 and len(self.differs) == 0

    @property
    def total_issues(self) -> int:
        """Total number of differences found."""
        return len(self.source_only) + len(self.target_only) + len(self.differs)
