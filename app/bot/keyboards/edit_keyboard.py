from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def edit_keyboard(deposit_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💰 Сумма",
                    callback_data=f"edit_amount_{deposit_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📈 Ставка",
                    callback_data=f"edit_rate_{deposit_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⏳ Срок",
                    callback_data=f"edit_months_{deposit_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Дата открытия",
                    callback_data=f"edit_date_{deposit_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Название вклада",
                    callback_data=f"edit_name_{deposit_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅ Назад",
                    callback_data=f"back_info_{deposit_id}"
                )
            ]
        ]
    )