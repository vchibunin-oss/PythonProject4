"""Functions for processing bank operations."""

from collections import Counter
import re
from typing import Any


def filter_by_state(
    operations: list[dict[str, Any]],
    state: str = "EXECUTED",
) -> list[dict[str, Any]]:
    """Return operations filtered by state."""
    return [
        operation
        for operation in operations
        if operation.get("state") == state
    ]


def sort_by_date(
    operations: list[dict[str, Any]],
    reverse: bool = True,
) -> list[dict[str, Any]]:
    """Return operations sorted by date."""
    return sorted(
        operations,
        key=lambda operation: operation.get("date", ""),
        reverse=reverse,
    )


def process_bank_search(
    data: list[dict[str, Any]],
    search: str,
) -> list[dict[str, Any]]:
    """Search bank operations by description."""
    return [
        operation
        for operation in data
        if re.search(
            search,
            operation.get("description", ""),
            re.IGNORECASE,
        )
    ]


def process_bank_operations(
    data: list[dict[str, Any]],
    categories: list[str],
) -> dict[str, int]:
    """Count bank operations by category."""
    descriptions = [
        operation.get("description", "")
        for operation in data
    ]

    counter = Counter()

    for category in categories:
        counter[category] = sum(
            1
            for description in descriptions
            if category.lower() in description.lower()
        )

    return dict(counter)