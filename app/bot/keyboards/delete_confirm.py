from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def delete_confirm_keyboard(
        deposit_id: int
):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"confirm_delete_{deposit_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="↩ Отмена",
                    callback_data="cancel_delete"
                )
            ]
        ]
    )