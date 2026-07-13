import pytest

from src.widget import get_date, mask_account_card


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Visa Platinum 1234567812345678", "Visa Platinum 1234 56** **** 5678"),
        ("Счет 12345678901234567890", "Счет **7890"),
    ],
)
def test_mask_account_card(text, expected):
    assert mask_account_card(text) == expected


def test_get_date():
    assert get_date("2024-07-14T12:00:00") == "14.07.2024"
