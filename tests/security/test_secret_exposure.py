"""Security tests — ensure secrets are never exposed in output."""

from piped.models import Variable


class TestSecretExposure:
    def test_secret_value_not_exposed_in_masked_output(self):
        var = Variable(key="DB_PASS", value="super_secret_123", is_secret=True)
        assert "super_secret_123" not in var.masked_value()

    def test_secret_value_not_exposed_in_repr(self):
        var = Variable(key="DB_PASS", value="super_secret_123", is_secret=True)
        assert "super_secret_123" not in repr(var)

    def test_non_secret_exposed_in_masked_output(self):
        var = Variable(key="REGION", value="us-east-1", is_secret=False)
        assert "us-east-1" in var.masked_value()

    def test_none_value_not_exposed(self):
        var = Variable(key="MISSING", value=None, is_secret=True)
        assert var.masked_value() == "(not set)"

    def test_masked_value_constant_regardless_of_length(self):
        short = Variable(key="A", value="x", is_secret=True)
        long = Variable(key="B", value="x" * 100, is_secret=True)
        assert short.masked_value() == long.masked_value() == "••••••••"
