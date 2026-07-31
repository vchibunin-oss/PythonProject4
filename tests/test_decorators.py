import pytest

from src.decorators import log


def test_log_to_console(capsys: pytest.CaptureFixture[str]) -> None:
    @log()
    def add_numbers(a: int, b: int) -> int:
        return a + b

    result = add_numbers(2, 3)
    captured = capsys.readouterr()

    assert result == 5
    assert "add_numbers ok" in captured.out


def test_log_to_file(tmp_path) -> None:
    log_file = tmp_path / "test_log.txt"

    @log(filename=str(log_file))
    def multiply_numbers(a: int, b: int) -> int:
        return a * b

    result = multiply_numbers(4, 5)

    assert result == 20
    assert "multiply_numbers ok" in log_file.read_text(encoding="utf-8")


def test_log_error_to_console(capsys: pytest.CaptureFixture[str]) -> None:
    @log()
    def divide_numbers(a: int, b: int) -> float:
        return a / b

    with pytest.raises(ZeroDivisionError):
        divide_numbers(10, 0)

    captured = capsys.readouterr()

    assert "divide_numbers error: ZeroDivisionError" in captured.out
    assert "Inputs: (10, 0), {}" in captured.out


def test_log_error_to_file(tmp_path) -> None:
    log_file = tmp_path / "error_log.txt"

    @log(filename=str(log_file))
    def divide_numbers(a: int, b: int) -> float:
        return a / b

    with pytest.raises(ZeroDivisionError):
        divide_numbers(10, 0)

    log_text = log_file.read_text(encoding="utf-8")

    assert "divide_numbers error: ZeroDivisionError" in log_text
    assert "Inputs: (10, 0), {}" in log_text
