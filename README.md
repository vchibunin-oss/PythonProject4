# PythonProject4

## Описание

Проект содержит функции для обработки банковских операций.

Реализованы следующие функции:
- фильтрация списка словарей по статусу операции;
- сортировка операций по дате;
- маскирование номеров карт и счетов;
- получение даты в удобном формате.

- filter_by_state — фильтрует список словарей по значению ключа state.
- sort_by_date — сортирует список словарей по дате.

## Установка

1. Клонировать репозиторий:
git clone <ссылка_на_репозиторий>
2. Установить зависимости:
poetry install
## Запуск

Для запуска тестов:
pytest
git clone <ссылка на репозиторий>
2. Перейти в папку проекта:
cd PythonProject4
3. Установить зависимости:
poetry install
## Использование
from src.processing import filter_by_state, sort_by_date

result = filter_by_state(data)
sorted_data = sort_by_date(data)
## Модуль generators

Модуль generators содержит функции для работы с транзакциями и номерами банковских карт.

### filter_by_currency

Функция принимает список транзакций и код валюты. Возвращает итератор с транзакциями в указанной валюте.
from src.generators import filter_by_currency

usd_transactions = filter_by_currency(transactions, "USD")
### transaction_descriptions

Функция-генератор по очереди возвращает описания транзакций.
from src.generators import transaction_descriptions

descriptions = transaction_descriptions(transactions)
### card_number_generator

Генератор создает номера банковских карт в формате XXXX XXXX XXXX XXXX в заданном диапазоне.
from src.generators import card_number_generator

card_numbers = card_number_generator(1, 3)

for card_number in card_numbers:
    print(card_number)
## Автор

Владимир
