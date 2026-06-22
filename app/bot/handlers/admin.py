from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from app.config.config import ADMINS

from app.database.models.user import User

from app.bot.states.admin import (
    Broadcast
)

from app.config.config import (
    Config
)

from aiogram import Bot

from aiogram.fsm.context import (
    FSMContext
)

from sqlalchemy import select

from app.database.models.user import (
    User
)

from app.database.database import (
    async_session
)

from app.database.database import async_session
from app.database.models.deposit import Deposit


router = Router()


@router.message(Command("broadcast"))
async def broadcast_start(
        message: Message,
        state: FSMContext
):
    if message.from_user.id != Config.ADMIN_ID:
        return

    await state.set_state(
        Broadcast.message
    )

    await message.answer(
        "Введите сообщение для рассылки"
    )


@router.message(Broadcast.message)
async def send_broadcast(
        message: Message,
        state: FSMContext
):
    if message.from_user.id != Config.ADMIN_ID:
        return

    async with async_session() as session:

        query = select(User.telegram_id)

        result = await session.execute(query)

        users = result.scalars().all()

    success = 0

    for user_id in users:

        try:

            await message.bot.send_message(
                user_id,
                f"📢 Рассылка\n\n"
                f"{message.text}"
            )

            success += 1

        except Exception:
            pass

    await message.answer(
        f"✅ Отправлено: {success}"
    )

    await state.clear()