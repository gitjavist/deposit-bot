from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def wizard_keyboard(
        step: str
):
    return InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(
                    text="⬅ Назад",
                    callback_data=f"wizard_back_{step}"
                ),

                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_add_deposit"
                )

            ]

        ]
    )