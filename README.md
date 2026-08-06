# PythonProject4

## Описание

Проект содержит функции для обработки банковских операций.

### Реализованные функции

- Фильтрация списка операций по статусу.
- Сортировка операций по дате.
- Маскирование номеров карт и счетов.
- Форматирование даты.
- Работа с генераторами.
- Чтение данных из CSV-файлов.
- Чтение данных из Excel-файлов.

## Установка

1. Клонировать репозиторий:
git clone <ссылка_на_репозиторий>2. Перейти в папку проекта:
cd PythonProject43. Установить зависимости:
poetry install## Запуск

Запуск тестов:
pytest## Использование
from src.processing import filter_by_state, sort_by_date

result = filter_by_state(data)
sorted_data = sort_by_date(data)## Модуль generators

### filter_by_currency

Возвращает генератор транзакций по указанной валюте.
from src.generators import filter_by_currency

usd_transactions = filter_by_currency(transactions, "USD")### transaction_descriptions

Возвращает описания транзакций.
from src.generators import transaction_descriptions

descriptions = transaction_descriptions(transactions)### card_number_generator

Генерирует номера банковских карт в указанном диапазоне.
from src.generators import card_number_generator

for card in card_number_generator(1, 3):
    print(card)## Новая функциональность

Добавлена поддержка чтения финансовых операций из файлов CSV и Excel.

### Чтение CSV
from src.csv_excel import read_csv

transactions = read_csv("data/transactions.csv")### Чтение Excel
from src.csv_excel import read_excel

transactions = read_excel("data/transactions.xlsx")## Автор

Владимир Чибунин