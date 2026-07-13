from src.processing import filter_by_state, sort_by_date


def test_filter_by_state(operations):
    result = filter_by_state(operations)

    assert len(result) == 2
    assert all(item["state"] == "EXECUTED" for item in result)


def test_filter_by_state_canceled(operations):
    result = filter_by_state(operations, "CANCELED")

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