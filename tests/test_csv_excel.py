"""Тесты для модуля чтения CSV и Excel файлов."""

from pathlib import Path

from csv_excel import read_csv, read_excel


def test_read_csv(tmp_path: Path):
    file_path = tmp_path / 'operations.csv'
    file_path.write_text(
        'id;state;description\n'
        '1;EXECUTED;Перевод\n'
        '2;CANCELED;Открытие счета\n'
    )

    result = read_csv(str(file_path))

    assert len(result) == 2
    assert result[0]['id'] == 1
    assert result[0]['state'] == 'EXECUTED'
    assert result[0]['description'] == 'Перевод'


def test_read_excel(tmp_path: Path):
    import pandas as pd

    file_path = tmp_path / 'operations.xlsx'

    dataframe = pd.DataFrame(
        [
            {
                'id': 1,
                'state': 'EXECUTED',
                'description': 'Перевод',
            },
            {
                'id': 2,
                'state': 'CANCELED',
                'description': 'Открытие счета',
            },
        ]
    )

    dataframe.to_excel(file_path, index=False)

    result = read_excel(str(file_path))

    assert len(result) == 2
    assert result[0]['id'] == 1
    assert result[0]['state'] == 'EXECUTED'
    assert result[0]['description'] == 'Перевод'
