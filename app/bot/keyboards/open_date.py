from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

open_date_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📅 Сегодня",
                callback_data="date_today"
            )
        ],
        [
            InlineKeyboardButton(
                text="✏ Ввести дату",
                callback_data="deposit_custom_date"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅ Назад",
                callback_data="wizard_back_months"
            ),

            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel_add_deposit"
            )
        ]
    ]
)