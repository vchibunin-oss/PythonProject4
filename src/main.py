from pathlib import Path

from processing import filter_by_state, process_bank_search
from utils import load_transactions


def main():
    print("Добро пожаловать в программу работы с банковскими операциями!")

    file_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "operations.json"
    )

    operations = load_transactions(str(file_path))

    if not operations:
        print("Не удалось загрузить банковские операции.")
        return

    print("\nФильтруем операции по статусу EXECUTED...")
    operations = filter_by_state(operations)

    search = input(
        "\nВведите строку для поиска банковских операций: "
    ).strip()

    if search:
        print(f'\nИщем операции по запросу: "{search}"')
        operations = process_bank_search(operations, search)

    if operations:
        print(f"\nНайдено операций: {len(operations)}")
        print("Результаты поиска:\n")

        for operation in operations:
            print(
                f"Дата: {operation.get('date', '')} | "
                f"Описание: {operation.get('description', '')} | "
                f"Откуда: {operation.get('from', '')} | "
                f"Куда: {operation.get('to', '')}"
            )
    else:
        print("\nОпераций, соответствующих запросу, не найдено.")


if __name__ == "__main__":
    main()
