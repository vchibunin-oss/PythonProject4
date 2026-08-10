from src.processing import (
    filter_by_state,
    process_bank_operations,
    process_bank_search,
    sort_by_date,
)


def test_filter_by_state(operations):
    result = filter_by_state(operations)

    assert len(result) == 2
    assert all(item["state"] == "EXECUTED" for item in result)


def test_filter_by_state_canceled(operations):
    result = filter_by_state(operations, state="CANCELED")

    assert len(result) == 1
    assert result[0]["state"] == "CANCELED"


def test_sort_by_date_desc(operations):
    result = sort_by_date(operations)

    assert result[0]["date"] == "2024-01-03"
    assert result[-1]["date"] == "2024-01-01"


def test_sort_by_date_asc(operations):
    result = sort_by_date(operations, reverse=False)

    assert result[0]["date"] == "2024-01-01"
    assert result[-1]["date"] == "2024-01-03"


def test_process_bank_search(operations):
    result = process_bank_search(operations, "перевод")

    assert len(result) == 2

    for operation in result:
        assert "перевод" in operation["description"].lower()


def test_process_bank_search_case_insensitive(operations):
    result = process_bank_search(operations, "ПЕРЕВОД")

    assert len(result) == 2


def test_process_bank_search_no_results(operations):
    result = process_bank_search(operations, "несуществующая операция")

    assert result == []


def test_process_bank_operations(operations):
    result = process_bank_operations(
        operations,
        ["перевод", "открытие"],
    )

    assert result["перевод"] == 2
    assert result["открытие"] == 1


def test_process_bank_operations_empty_categories(operations):
    result = process_bank_operations(operations, [])

    assert result == {}