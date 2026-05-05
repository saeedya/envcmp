"""Unit tests for base provider."""

import pytest

from envcmp.models import Variable
from envcmp.providers.base import BaseProvider


class ConcreteProvider(BaseProvider):
    """A minimal concrete implementation for testing."""

    def __init__(self, variables: list[Variable]) -> None:
        self._variables = variables

    def list(self) -> list[Variable]:
        return self._variables

    def write(self, variable: Variable) -> None:
        self._variables.append(variable)

    def delete(self, key: str) -> None:
        self._variables = [v for v in self._variables if v.key != key]


class TestBaseProvider:
    def test_list_returns_variables(self):
        provider = ConcreteProvider([Variable("KEY", "value")])
        assert len(provider.list()) == 1

    def test_write_adds_variable(self):
        provider = ConcreteProvider([])
        provider.write(Variable("NEW_KEY", "new_value"))
        assert len(provider.list()) == 1

    def test_delete_removes_variable(self):
        provider = ConcreteProvider([Variable("KEY", "value")])
        provider.delete("KEY")
        assert len(provider.list()) == 0

    def test_cannot_instantiate_base_provider_directly(self):
        with pytest.raises(TypeError):
            BaseProvider()  # type: ignore
