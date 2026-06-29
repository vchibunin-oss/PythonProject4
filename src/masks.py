def get_mask_card_number(card_number: str) -> str:
    return (
        f"{card_number[:4]} "
        f"{card_number[4:6]}** **** "
        f"{card_number[-4:]}"
    )


def get_mask_account(account_number: str) -> str:
    return f"**{account_number[-4:]}"