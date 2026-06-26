from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(data: str) -> str:
    parts = data.split()
    number = parts[-1]
    name = " ".join(parts[:-1])

    if name == "Счет":
        return f"{name} {get_mask_account(number)}"

    return f"{name} {get_mask_card_number(number)}"

    def format_date(date: str) -> str:
        return f"{date[8:10]}.{date[5:7]}.{date[0:4]}"