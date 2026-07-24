"""Functions for processing bank operations."""

from typing import Any


def filter_by_state(
    operations: list[dict[str, Any]],
    state: str = "EXECUTED",
) -> list[dict[str, Any]]:
    """
    Return operations filtered by state.
    """
    return [
        operation
        for operation in operations
        if operation.get("state") == state
    ]


def sort_by_date(
    operations: list[dict[str, Any]],
    reverse: bool = True,
) -> list[dict[str, Any]]:
    """
    Return operations sorted by date.
    """
    return sorted(
        operations,
        key=lambda operation: operation["date"],
        reverse=reverse,
    )
