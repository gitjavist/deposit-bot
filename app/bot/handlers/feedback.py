from aiogram import (
    Router,
    F,
    Bot
)

from aiogram.types import (
    CallbackQuery,
    Message
)

from aiogram.fsm.context import (
    FSMContext
)

from app.bot.states.feedback import (
    Feedback
)

from app.config.config import (
    Config
)

router = Router()


@router.callback_query(
    F.data == "feedback"
)
async def feedback_start(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.set_state(
        Feedback.message
    )

    await callback.message.answer(
        "✉ Напишите ваше сообщение"
    )

    await callback.answer()


@router.message(
    Feedback.message
)
async def feedback_send(
        message: Message,
        state: FSMContext,
        bot: Bot
):
    await bot.send_message(
        chat_id=Config.ADMIN_ID,

        text=(
            f"✉ Новая обратная связь\n\n"

            f"👤 Пользователь:\n"
            f"{message.from_user.full_name}\n"

            f"🆔 ID:\n"
            f"{message.from_user.id}\n\n"

            f"💬 Сообщение:\n"
            f"{message.text}"
        )
    )

    await message.answer(
        "✅ Сообщение отправлено"
    )

    await state.clear()