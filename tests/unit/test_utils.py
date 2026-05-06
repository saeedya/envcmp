"""Unit tests for utils.py"""

from envcmp.models import Variable
from envcmp.utils import filter_variables


class TestFilterVariables:
    def test_no_filter_returns_all(self):
        variables = [Variable("DB_HOST", "localhost"), Variable("API_KEY", "abc")]
        result = filter_variables(variables, None)
        assert len(result) == 2

    def test_exact_match(self):
        variables = [Variable("DB_HOST", "localhost"), Variable("API_KEY", "abc")]
        result = filter_variables(variables, "API_KEY")
        assert len(result) == 1
        assert result[0].key == "API_KEY"

    def test_wildcard_prefix(self):
        variables = [
            Variable("DB_HOST", "localhost"),
            Variable("DB_PORT", "5432"),
            Variable("API_KEY", "abc"),
        ]
        result = filter_variables(variables, "DB_*")
        assert len(result) == 2
        assert all(v.key.startswith("DB_") for v in result)

    def test_multiple_patterns(self):
        variables = [
            Variable("DB_HOST", "localhost"),
            Variable("API_KEY", "abc"),
            Variable("REGION", "us-east-1"),
        ]
        result = filter_variables(variables, "DB_*,API_*")
        assert len(result) == 2

    def test_no_match_returns_empty(self):
        variables = [Variable("DB_HOST", "localhost")]
        result = filter_variables(variables, "AWS_*")
        assert len(result) == 0

    def test_pattern_with_spaces(self):
        variables = [Variable("DB_HOST", "localhost"), Variable("API_KEY", "abc")]
        result = filter_variables(variables, "DB_* , API_*")
        assert len(result) == 2
