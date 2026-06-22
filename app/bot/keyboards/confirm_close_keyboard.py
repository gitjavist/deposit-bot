from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def confirm_close_keyboard(
        deposit_id: int
):
    return InlineKeyboardMarkup(

        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data=f"confirm_close_{deposit_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data=f"back_{deposit_id}"
                )
            ]
        ]
    )