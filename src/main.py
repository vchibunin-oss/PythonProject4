from pathlib import Path
import re

from csv_excel import read_csv, read_excel
from processing import filter_by_state, process_bank_search, sort_by_date
from utils import load_transactions
from widget import mask_account_card, get_date

RUB_CODES = ("RUB", "RUR")


def load_file(file_path: Path, source: str) -> list[dict]:
    """Загружает операции из выбранного источника."""
    if source == "1":
        return load_transactions(str(file_path))
    if source == "2":
        return read_csv(str(file_path))
    if source == "3":
        return read_excel(str(file_path))
    return []


def is_ruble_operation(operation: dict) -> bool:
    """Проверяет, является ли операция рублевой."""
    operation_amount = operation.get("operationAmount", {})

    if isinstance(operation_amount, dict):
        currency = operation_amount.get("currency", {})
        if isinstance(currency, dict):
            code = currency.get("code", "")
            if str(code).upper() in RUB_CODES:
                return True

    currency = operation.get("currency", {})
    if isinstance(currency, dict):
        code = currency.get("code", "")
        if str(code).upper() in RUB_CODES:
            return True

    if str(operation.get("currency_code", "")).upper() in RUB_CODES:
        return True

    return str(currency).upper() in RUB_CODES


def format_amount(operation: dict) -> str:
    """Форматирует сумму операции с учетом валюты."""
    amount = operation.get("amount", "")
    currency_code = str(operation.get("currency_code", "")).upper()
    if currency_code in RUB_CODES:
        return f"Сумма: {amount} руб."
    return f"Сумма: {amount} {currency_code}"


def print_operations(operations: list[dict]) -> None:
    """Выводит найденные банковские операции."""
    if not operations:
        print("\nОпераций, соответствующих запросу, не найдено.")
        return

    print(f"\nНайдено операций: {len(operations)}")
    print("Результат поиска:\n")

    for operation in operations:
        date_raw = operation.get("date", "")
        description = operation.get("description", "")
        from_raw = operation.get("from", "")
        to_raw = operation.get("to", "")

        date_str = get_date(date_raw) if date_raw else ""
        from_str = mask_account_card(from_raw) if from_raw else ""
        to_str = mask_account_card(to_raw) if to_raw else ""

        print(f"{date_str} {description}")
        if from_str and to_str:
            print(f"{from_str} -> {to_str}")
        else:
            print(from_str or to_str)

        print(format_amount(operation))
        print()


def main() -> None:
    print("Программа: Привет! Добро пожаловать в программу работы")
    print("с банковскими транзакциями.")

    print("\nВыберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    source = input("\nПользователь: ").strip()

    data_dir = Path(__file__).resolve().parent.parent / "data"

    if source == "1":
        file_path = data_dir / "operations.json"
        print("Программа: Для обработки выбран JSON-файл.")
    elif source == "2":
        file_path = data_dir / "operations.csv"
        print("Программа: Для обработки выбран CSV-файл.")
    elif source == "3":
        file_path = data_dir / "operations.xlsx"
        print("Программа: Для обработки выбран XLSX-файл.")
    else:
        print("Программа: Неверный пункт меню.")
        return

    try:
        operations = load_file(file_path, source)
    except (FileNotFoundError, ValueError, OSError):
        print(f"Программа: Файл не найден: {file_path}")
        return

    if not operations:
        print("Программа: Не удалось загрузить банковские операции.")
        return

    print("\nПрограмма: Введите статус, по которому необходимо выполнить фильтрацию.")
    print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")

    status = input("Пользователь: ").strip().upper()

    while status not in ("EXECUTED", "CANCELED", "PENDING"):
        print("Программа: Введите один из доступных статусов:")
        print("EXECUTED, CANCELED, PENDING")
        status = input("Пользователь: ").strip().upper()

    operations = filter_by_state(operations, status)

    print(f'\nПрограмма: Операции отфильтрованы по статусу "{status}"')

    sort_answer = input(
        "\nПрограмма: Отсортировать операции по дате? Да/Нет\n"
        "Пользователь: "
    ).strip().lower()

    if sort_answer in ("да", "д", "yes", "y"):
        sort_direction = input(
            "\nПрограмма: Отсортировать по возрастанию "
            "или по убыванию?\n"
            "Пользователь: "
        ).strip().lower()

        if "возрастан" in sort_direction:
            operations = sort_by_date(operations, reverse=False)
        else:
            operations = sort_by_date(operations, reverse=True)

    ruble_answer = input(
        "\nПрограмма: Выводить только рублевые транзакции? Да/Нет\n"
        "Пользователь: "
    ).strip().lower()

    if ruble_answer in ("да", "д", "yes", "y"):
        operations = [
            operation
            for operation in operations
            if is_ruble_operation(operation)
        ]

    search_answer = input(
        "\nПрограмма: Фильтровать список транзакций по определенному "
        "слову в описании? Да/Нет\n"
        "Пользователь: "
    ).strip().lower()

    if search_answer in ("да", "д", "yes", "y"):
        search_word = input(
            "\nПрограмма: Введите слово для поиска в описании:\n"
            "Пользователь: "
        ).strip()

        if search_word:
            operations = process_bank_search(
                operations,
                re.escape(search_word),
            )

    print_operations(operations)


if __name__ == "__main__":
    main()
