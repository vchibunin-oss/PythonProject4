import json

from src.utils import load_transactions


def test_load_transactions_success(tmp_path):
    data = [{"id": 1}, {"id": 2}]
    file = tmp_path / "test.json"

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    assert load_transactions(file) == data


def test_load_transactions_file_not_found():
    assert load_transactions("no_file.json") == []


def test_load_transactions_empty_file(tmp_path):
    file = tmp_path / "empty.json"
    file.write_text("")

    assert load_transactions(file) == []


def test_load_transactions_not_list(tmp_path):
    file = tmp_path / "dict.json"

    with open(file, "w", encoding="utf-8") as f:
        json.dump({"id": 1}, f)

    assert load_transactions(file) == []
