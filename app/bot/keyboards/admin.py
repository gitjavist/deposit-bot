from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

admin_keyboard = ReplyKeyboardMarkup(

    keyboard=[

        [
            KeyboardButton(
                text="📊 Статистика бота"
            )
        ],

        [
            KeyboardButton(
                text="📢 Рассылка"
            )
        ]

    ],

    resize_keyboard=True
)