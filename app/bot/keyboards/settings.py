from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def settings_keyboard(
        notifications_enabled: bool
):
    status = (
        "🔕 Выключить"
        if notifications_enabled
        else
        "🔔 Включить"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text=status,
                    callback_data="toggle_notifications"
                )
            ],
            [

                InlineKeyboardButton(
                    text="⏰ Изменить время",
                    callback_data="change_notification_hour"
                )

            ],
            [
                InlineKeyboardButton(
                    text="✉ Обратная связь",
                    callback_data="feedback"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📑 Вид отображения",
                    callback_data="open_view_settings"
                )
            ]

        ]
    )