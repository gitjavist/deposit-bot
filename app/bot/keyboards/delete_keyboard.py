from aiogram.utils.keyboard import (
    InlineKeyboardBuilder
)


def delete_keyboard(deposits):

    builder = InlineKeyboardBuilder()

    for deposit in deposits:

        builder.button(
            text=f"{deposit.bank} ({deposit.amount})",
            callback_data=f"delete_{deposit.id}"
        )

    builder.adjust(1)

    return builder.as_markup()