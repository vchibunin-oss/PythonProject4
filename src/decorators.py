from functools import wraps
from typing import Any, Callable


def log(filename: str | None = None) -> Callable:
    """Логирует результат выполнения функции или возникшую ошибку."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
                message = f"{func.__name__} ok\n"
            except Exception as error:
                message = (
                    f"{func.__name__} error: {type(error).__name__}. "
                    f"Inputs: {args}, {kwargs}\n"
                )

                if filename:
                    with open(filename, "a", encoding="utf-8") as file:
                        file.write(message)
                else:
                    print(message, end="")

                raise

            if filename:
                with open(filename, "a", encoding="utf-8") as file:
                    file.write(message)
            else:
                print(message, end="")

            return result

        return wrapper

    return decorator
