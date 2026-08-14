from pathlib import Path
import re

from csv_excel import read_csv, read_excel
from processing import filter_by_state, process_bank_search, sort_by_date
from utils import load_transactions


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
            if str(code).upper() in ("RUB", "RUR"):
                return True

    currency = operation.get("currency", {})
    if isinstance(currency, dict):
        code = currency.get("code", "")
        if str(code).upper() in ("RUB", "RUR"):
            return True

    if str(operation.get("currency_code", "")).upper() in ("RUB", "RUR"):
        return True

    return str(currency).upper() in ("RUB", "RUR")


def print_operations(operations: list[dict]) -> None:
    """Выводит найденные банковские операции."""
    if not operations:
        print("\nОпераций, соответствующих запросу, не найдено.")
        return

    print(f"\nНайдено операций: {len(operations)}")
    print("Результат поиска:\n")

    for operation in operations:
        print(
            f"Дата: {operation.get('date', '')} | "
            f"Описание: {operation.get('description', '')} | "
            f"Откуда: {operation.get('from', '')} | "
            f"Куда: {operation.get('to', '')}"
        )


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
    

