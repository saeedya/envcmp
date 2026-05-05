"""Unit tests for models.py"""

from envcmp.models import DiffResult, ProviderKind, Variable


class TestVariable:
    def test_masked_value_for_secret(self):
        var = Variable(key="DB_PASS", value="super_secret", is_secret=True)
        assert var.masked_value() == "••••••••"

    def test_masked_value_for_non_secret(self):
        var = Variable(key="REGION", value="us-east-1", is_secret=False)
        assert var.masked_value() == "us-east-1"

    def test_masked_value_when_none(self):
        var = Variable(key="MISSING", value=None)
        assert var.masked_value() == "(not set)"

    def test_equality_same_key_and_value(self):
        a = Variable(key="X", value="1")
        b = Variable(key="X", value="1")
        assert a == b

    def test_inequality_different_value(self):
        a = Variable(key="X", value="1")
        b = Variable(key="X", value="2")
        assert a != b

    def test_repr_masks_secret_value(self):
        var = Variable(key="DB_PASS", value="secret", is_secret=True)
        assert "secret" not in repr(var)
        assert "DB_PASS" in repr(var)

    def test_equality_ignores_is_secret_flag(self):
        a = Variable(key="X", value="1", is_secret=True)
        b = Variable(key="X", value="1", is_secret=False)
        assert a == b

    def test_equality_with_non_variable(self):
        var = Variable(key="X", value="1")
        assert var.__eq__("not a variable") == NotImplemented


class TestDiffResult:
    def test_is_clean_when_everything_in_sync(self):
        diff = DiffResult(in_sync=[Variable("A", "1")])
        assert diff.is_clean is True

    def test_not_clean_when_source_only(self):
        diff = DiffResult(source_only=[Variable("A", "1")])
        assert diff.is_clean is False

    def test_not_clean_when_target_only(self):
        diff = DiffResult(target_only=[Variable("A", "1")])
        assert diff.is_clean is False

    def test_not_clean_when_differs(self):
        diff = DiffResult(differs=[(Variable("A", "1"), Variable("A", "2"))])
        assert diff.is_clean is False

    def test_total_issues_counts_all(self):
        diff = DiffResult(
            source_only=[Variable("A", "1")],
            target_only=[Variable("B", "2"), Variable("C", "3")],
            differs=[(Variable("D", "x"), Variable("D", "y"))],
        )
        assert diff.total_issues == 4

    def test_total_issues_zero_when_clean(self):
        diff = DiffResult(in_sync=[Variable("A", "1")])
        assert diff.total_issues == 0


class TestProviderKind:
    def test_string_values(self):
        assert ProviderKind.GITLAB == "gitlab"
        assert ProviderKind.GITHUB == "github"
        assert ProviderKind.TERRAFORM == "terraform"
        assert ProviderKind.ENV_FILE == "env"
