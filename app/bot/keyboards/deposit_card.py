from aiogram.utils.keyboard import (
    InlineKeyboardBuilder
)


def deposit_card_keyboard(
        deposit_id: int,
        product_type: str = "deposit",
        is_closed: bool = False,
        details: bool = False
):
    builder = InlineKeyboardBuilder()

    if details:

        builder.button(
            text="⬅ Назад",
            callback_data=f"back_{deposit_id}"
        )

    else:

        builder.button(
            text="ℹ Подробнее",
            callback_data=f"info_{deposit_id}"
        )

    builder.button(
        text="✏ Изменить",
        callback_data=f"deposit_edit_{deposit_id}"
    )

    if (
            product_type == "savings"
            and not is_closed
    ):
        builder.button(
            text="✅ Закрыть счёт",
            callback_data=f"close_{deposit_id}"
        )

    builder.button(
        text="❌ Удалить",
        callback_data=f"delete_{deposit_id}"
    )

    builder.adjust(2, 1)

    return builder.as_markup()