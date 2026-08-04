import logging
from pathlib import Path

logs_dir = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

logger = logging.getLogger("masks")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler(logs_dir / "masks.log", mode="w", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def get_mask_card_number(card_number: str) -> str:
    """Возвращает замаскированный номер карты."""
    result = f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"
    logger.info("Маскирование номера карты выполнено успешно")
    return result


def get_mask_account(account_number: str) -> str:
    """Возвращает замаскированный номер счета."""
    result = f"**{account_number[-4:]}"
    logger.info("Маскирование номера счета выполнено успешно")
    return result