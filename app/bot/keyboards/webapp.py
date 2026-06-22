from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)

webapp_button = KeyboardButton(
    text="🌐 Личный кабинет",
    web_app=WebAppInfo(
        url="https://sad-donuts-repeat.loca.lt"
    )
)

webapp_keyboard = ReplyKeyboardMarkup(
    keyboard=[[webapp_button]],
    resize_keyboard=True
)