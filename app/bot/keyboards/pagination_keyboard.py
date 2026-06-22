from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def pagination_keyboard(
        current_index: int,
        total: int,
        prefix: str
):
    row = []

    if current_index > 0:

        row.append(

            InlineKeyboardButton(
                text="◀️",
                callback_data=(
                    f"{prefix}_{current_index - 1}"
                )
            )
        )

    row.append(

        InlineKeyboardButton(
            text=f"{current_index + 1}/{total}",
            callback_data="ignore"
        )
    )

    if current_index < total - 1:

        row.append(

            InlineKeyboardButton(
                text="▶️",
                callback_data=(
                    f"{prefix}_{current_index + 1}"
                )
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[row]
    )