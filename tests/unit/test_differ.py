"""Unit tests for differ.py"""

from piped.differ import diff
from piped.models import Variable
from piped.providers.base import BaseProvider


class FakeProvider(BaseProvider):
    """A fake provider for testing."""

    def __init__(self, variables: list[Variable]) -> None:
        self._variables = variables

    def list(self) -> list[Variable]:
        return self._variables

    def write(self, variable: Variable) -> None:
        self._variables.append(variable)

    def delete(self, key: str) -> None:
        self._variables = [v for v in self._variables if v.key != key]


class TestDiff:
    def test_all_in_sync(self):
        source = FakeProvider([Variable("KEY", "value")])
        target = FakeProvider([Variable("KEY", "value")])
        result = diff(source, target)
        assert result.is_clean is True
        assert len(result.in_sync) == 1

    def test_source_only(self):
        source = FakeProvider([Variable("KEY", "value")])
        target = FakeProvider([])
        result = diff(source, target)
        assert len(result.source_only) == 1
        assert result.source_only[0].key == "KEY"

    def test_target_only(self):
        source = FakeProvider([])
        target = FakeProvider([Variable("KEY", "value")])
        result = diff(source, target)
        assert len(result.target_only) == 1
        assert result.target_only[0].key == "KEY"

    def test_differs(self):
        source = FakeProvider([Variable("KEY", "old")])
        target = FakeProvider([Variable("KEY", "new")])
        result = diff(source, target)
        assert len(result.differs) == 1
        assert result.differs[0][0].value == "old"
        assert result.differs[0][1].value == "new"

    def test_mixed(self):
        source = FakeProvider(
            [
                Variable("A", "1"),
                Variable("B", "2"),
                Variable("C", "3"),
            ]
        )
        target = FakeProvider(
            [
                Variable("A", "1"),
                Variable("B", "changed"),
                Variable("D", "4"),
            ]
        )
        result = diff(source, target)
        assert len(result.in_sync) == 1
        assert len(result.differs) == 1
        assert len(result.source_only) == 1
        assert len(result.target_only) == 1
        assert result.total_issues == 3
