from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

capitalization_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да",
                callback_data="cap_yes"
            ),
            InlineKeyboardButton(
                text="❌ Нет",
                callback_data="cap_no"
            )
        ]
    ]
)