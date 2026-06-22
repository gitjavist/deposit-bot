from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[

        [
            KeyboardButton(
                text="➕ Добавить вклад"
            ),

            KeyboardButton(
                text="📋 Мои вклады"
            )
        ],

        [
            KeyboardButton(
                text="📊 Аналитика"
            ),

            KeyboardButton(
                text="🔥 Скоро"
            )
        ],

        [
            KeyboardButton(
                text="📂 Сортировка"
            ),

            KeyboardButton(
                text="⚙ Настройки"
            )
        ],

        [
            KeyboardButton(
                text="🌐 Личный кабинет",
                web_app=WebAppInfo(
                    url="https://deposit-bot-ggba.onrender.com"
                )
            )
        ]

    ],

    resize_keyboard=True
)