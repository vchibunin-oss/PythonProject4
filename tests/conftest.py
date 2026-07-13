import pytest


@pytest.fixture
def operations():
    return [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-03"},
        {"id": 2, "state": "CANCELED", "date": "2024-01-01"},
        {"id": 3, "state": "EXECUTED", "date": "2024-01-02"},
    ]