"""Utility functions for envcmp."""

import fnmatch

from envcmp.models import Variable


def filter_variables(variables: list[Variable], pattern: str | None) -> list[Variable]:
    """Filter variables by a glob pattern.

    Pattern examples:
        "DB_*"        — all variables starting with DB_
        "API_KEY"     — exact match
        "DB_*,API_*"  — multiple patterns separated by comma
    """
    if pattern is None:
        return variables

    patterns = [p.strip() for p in pattern.split(",")]
    return [var for var in variables if any(fnmatch.fnmatch(var.key, p) for p in patterns)]
