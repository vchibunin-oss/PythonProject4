# PythonProject4

## Описание

Проект содержит функции для обработки банковских операций.

Реализованы следующие функции:

- filter_by_state — фильтрует список словарей по значению ключа state.
- sort_by_date — сортирует список словарей по дате.

## Установка

1. Клонировать репозиторий:
git clone <ссылка на репозиторий>
2. Перейти в папку проекта:
cd PythonProject4
3. Установить зависимости:
poetry install
## Использование
from src.processing import filter_by_state, sort_by_date

result = filter_by_state(data)
sorted_data = sort_by_date(data)
## Автор

Владимир
