import json


def load_transactions(file_path: str) -> list:
    """
    Загружает список транзакций из JSON-файла.
    Если файл не найден, пустой или содержит не список,
    возвращает пустой список.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (FileNotFoundError, json.JSONDecodeError):
        return []