from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


banks_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🟢 Сбер",
                callback_data="bank_СБЕР"
            )
        ],
        [
            InlineKeyboardButton(
                text="🟡 Т-Банк",
                callback_data="bank_Т-Банк"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔴 Альфа",
                callback_data="bank_Альфа"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔵 ВТБ",
                callback_data="bank_ВТБ"
            )
        ],
        [
            InlineKeyboardButton(
                text="➕ Другой банк",
                callback_data="bank_СвойБанк"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel_add_deposit"
            )
        ]
    ]
)