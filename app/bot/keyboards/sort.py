from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

sort_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💰 По сумме",
                callback_data="sort_amount"
            )
        ],
        [
            InlineKeyboardButton(
                text="📈 По ставке",
                callback_data="sort_rate"
            )
        ],
        [
            InlineKeyboardButton(
                text="📅 По сроку",
                callback_data="sort_months"
            )
        ]
    ]
)