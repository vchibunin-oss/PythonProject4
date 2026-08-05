"""Модуль для чтения финансовых операций из CSV и Excel файлов."""

from typing import Any

import pandas as pd


def read_csv(path: str) -> list[dict[str, Any]]:
    """
    Считывает финансовые операции из CSV-файла.

    :param path: Путь к CSV-файлу.
    :return: Список словарей с транзакциями.
    """
    dataframe = pd.read_csv(path)
    return dataframe.fillna("").to_dict(orient="records")


def read_excel(path: str) -> list[dict[str, Any]]:
    """
    Считывает финансовые операции из Excel-файла.

    :param path: Путь к Excel-файлу.
    :return: Список словарей с транзакциями.
    """
    dataframe = pd.read_excel(path)
    return dataframe.fillna("").to_dict(orient="records")