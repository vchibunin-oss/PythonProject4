import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")


def convert_transaction_to_rub(transaction: dict) -> float:
    """
    Возвращает сумму транзакции в рублях.
    Для USD и EUR выполняет конвертацию через API.
    """
    amount = float(transaction["operationAmount"]["amount"])
    currency = transaction["operationAmount"]["currency"]["code"]

    if currency == "RUB":
        return amount

    url = "https://api.apilayer.com/exchangerates_data/convert"

    headers = {"apikey": API_KEY}

    params = {"from": currency, "to": "RUB", "amount": amount}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    return float(data["result"])
