import json
import logging
from pathlib import Path

logs_dir = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler(logs_dir / "utils.log", mode="w", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


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
            logger.info("Транзакции успешно загружены")
            return data

        logger.error("JSON не содержит список")
        return []

    except FileNotFoundError:
        logger.error("Файл не найден")
        return []

    except json.JSONDecodeError:
        logger.error("Ошибка чтения JSON")
        return []