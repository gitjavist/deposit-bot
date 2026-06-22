from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.menu import main_keyboard

from sqlalchemy import select

from app.database.database import async_session
from app.database.models.user import User

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):

    async with async_session() as session:

        query = select(User).where(
            User.telegram_id
            == message.from_user.id
        )

        result = await session.execute(query)

        user = result.scalar()

        if not user:

            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )

            session.add(user)

            await session.commit()

    await message.answer(
        "🚀 Бот учета вкладов запущен!",
        reply_markup=main_keyboard
    )


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "/start - запуск\n"
        "/help - помощь"
    )