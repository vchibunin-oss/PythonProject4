import pytest


@pytest.fixture
def operations():
    return [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2024-01-03",
            "description": "Перевод",
        },
        {
            "id": 2,
            "state": "CANCELED",
            "date": "2024-01-01",
            "description": "Открытие счета",
        },
        {
            "id": 3,
            "state": "EXECUTED",
            "date": "2024-01-02",
            "description": "Перевод",
        },
    ]
