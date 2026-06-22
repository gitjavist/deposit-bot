from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

products_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🏦 Вклады",
                callback_data="products_deposits"
            )
        ],
        [
            InlineKeyboardButton(
                text="💳 Накопительные счета",
                callback_data="products_savings"
            )
        ],
        [
            InlineKeyboardButton(
                text="📂 Завершённые продукты",
                callback_data="products_closed"
            )
        ]
    ]
)