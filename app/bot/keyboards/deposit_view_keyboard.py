from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

deposit_view_keyboard = InlineKeyboardMarkup(

    inline_keyboard=[

        [

            InlineKeyboardButton(
                text="📜 Списком",
                callback_data="view_list"
            )

        ],

        [

            InlineKeyboardButton(
                text="📑 Постранично",
                callback_data="view_pagination"
            )

        ]

    ]
)