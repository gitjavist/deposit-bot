from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

product_type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏦 Вклад")],
        [KeyboardButton(text="💳 Накопительный счет")]
    ],
    resize_keyboard=True
)