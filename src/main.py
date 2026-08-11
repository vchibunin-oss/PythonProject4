from pathlib import Path

from processing import filter_by_state, process_bank_search
from utils import load_transactions


def main():
    print("Добро пожаловать в программу работы с банковскими операциями!")

    file_path = Path(__file__).resolve().parent.parent / "data" / "operations.json"
    operations = load_transactions(str(file_path))

    if not operations:
        print("Не удалось загрузить банковские операции.")
        return

    operations = filter_by_state(operations)

    search = input(
        "Введите строку для поиска банковских операций "
        "(или нажмите Enter для просмотра всех операций): "
    ).strip()

    if search:
        operations = process_bank_search(operations, search)

    if operations:
        print(f"\nНайдено операций: {len(operations)}")
        for operation in operations:
            print(
                f"{operation.get('date', '')} | "
                f"{operation.get('description', '')} | "
                f"{operation.get('from', '')} -> "
                f"{operation.get('to', '')}"
            )
    else:
        print("Операций, соответствующих запросу, не найдено.")


if __name__ == "__main__":
     main()

