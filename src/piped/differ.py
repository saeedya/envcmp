"""Diff logic between two providers."""

from piped.models import Variable, DiffResult
from piped.providers.base import BaseProvider


def diff(source: BaseProvider, target: BaseProvider) -> DiffResult:
    """Compare variables between source and target providers.

    Returns a DiffResult showing what is in sync, missing, or different.
    """
    source_vars = {v.key: v for v in source.list()}
    target_vars = {v.key: v for v in target.list()}

    result = DiffResult()

    for key, source_var in source_vars.items():
        if key not in target_vars:
            result.source_only.append(source_var)
        elif source_var == target_vars[key]:
            result.in_sync.append(source_var)
        else:
            result.differs.append((source_var, target_vars[key]))

    for key, target_var in target_vars.items():
        if key not in source_vars:
            result.target_only.append(target_var)

    return result