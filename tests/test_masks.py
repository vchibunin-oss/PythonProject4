import pytest

from src.masks import get_mask_account, get_mask_card_number


@pytest.mark.parametrize(
    "card, expected",
    [
        ("1234567812345678", "1234 56** **** 5678"),
        ("1111222233334444", "1111 22** **** 4444"),
    ],
)
def test_get_mask_card_number(card, expected):
    assert get_mask_card_number(card) == expected


@pytest.mark.parametrize(
    "account, expected",
    [
        ("12345678901234567890", "**7890"),
        ("1111222233334444", "**4444"),
    ],
)
def test_get_mask_account(account, expected):
    assert get_mask_account(account) == expected
