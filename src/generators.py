from collections.abc import Generator, Iterator


def filter_by_currency(
    transactions: list[dict],
    currency: str,
) -> Iterator[dict]:
    """Возвращает транзакции с указанной валютой."""

    return (
        transaction
        for transaction in transactions
        if transaction["operationAmount"]["currency"]["code"] == currency
    )


def transaction_descriptions(
    transactions: list[dict],
) -> Generator[str, None, None]:
    """Поочередно возвращает описания транзакций."""

    for transaction in transactions:
        yield transaction["description"]


def card_number_generator(
    start: int,
    end: int,
) -> Generator[str, None, None]:
    """Генерирует номера банковских карт в заданном диапазоне."""

    for number in range(start, end + 1):
        card_number = f"{number:016d}"

        yield (
            f"{card_number[:4]} "
            f"{card_number[4:8]} "
            f"{card_number[8:12]} "
            f"{card_number[12:]}"
        )
