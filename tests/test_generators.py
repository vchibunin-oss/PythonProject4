import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions


@pytest.fixture
def transactions():
    return [
        {
            "description": "Перевод организации",
            "operationAmount": {
                "currency": {"code": "USD"}
            },
        },
        {
            "description": "Оплата картой",
            "operationAmount": {
                "currency": {"code": "RUB"}
            },
        },
        {
            "description": "Перевод клиенту",
            "operationAmount": {
                "currency": {"code": "USD"}
            },
        },
    ]


@pytest.mark.parametrize(
    "currency, expected",
    [
        ("USD", 2),
        ("RUB", 1),
    ],
)
def test_filter_by_currency(transactions, currency, expected):
    result = list(filter_by_currency(transactions, currency))
    assert len(result) == expected


def test_transaction_descriptions(transactions):
    result = list(transaction_descriptions(transactions))
    assert result == [
        "Перевод организации",
        "Оплата картой",
        "Перевод клиенту",
    ]


@pytest.mark.parametrize(
    "start, end, expected",
    [
        (1, 1, ["0000 0000 0000 0001"]),
        (9998, 10000, [
            "0000 0000 0000 9998",
            "0000 0000 0000 9999",
            "0000 0000 0001 0000",
        ]),
    ],
)
def test_card_number_generator(start, end, expected):
    result = list(card_number_generator(start, end))
    assert result == expected
