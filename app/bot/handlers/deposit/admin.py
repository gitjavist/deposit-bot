from app.core.imports import *

router = Router()

@router.message(Command("admin"))
async def admin_panel(
        message: Message
):
    if not is_admin(
        message.from_user.id
    ):
        return

    await message.answer(
        "⚙ Admin panel",
        reply_markup=admin_keyboard
    )


@router.message(
    F.text == "📊 Статистика бота"
)
async def bot_stats(
        message: Message
):
    if not is_admin(
        message.from_user.id
    ):
        return

    async with async_session() as session:

        users_query = select(User)

        users_result = await session.execute(
            users_query
        )

        users = users_result.scalars().all()

        deposits_query = select(Deposit)

        deposits_result = await session.execute(
            deposits_query
        )

        deposits = deposits_result.scalars().all()

    total_amount = Decimal("0")

    for deposit in deposits:

        total_amount += deposit.amount

    text = (
        f"📊 <b>Статистика бота</b>\n\n"

        f"👥 Пользователей:\n"
        f"<b>{len(users)}</b>\n\n"

        f"🏦 Вкладов:\n"
        f"<b>{len(deposits)}</b>\n\n"

        f"💰 Общая сумма:\n"
        f"<b>{total_amount:,.2f} ₽</b>"
    )

    await message.answer(text)


@router.message(
    F.text == "📢 Рассылка"
)
async def broadcast_start(
        message: Message,
        state: FSMContext
):
    if not is_admin(
        message.from_user.id
    ):
        return

    await state.set_state(
        Broadcast.message
    )

    await message.answer(
        "📢 Отправьте сообщение для рассылки"
    )



@router.message(Broadcast.message)
async def process_broadcast(
        message: Message,
        state: FSMContext,
        bot: Bot
):
    if not is_admin(
        message.from_user.id
    ):
        return

    async with async_session() as session:

        query = select(User)

        result = await session.execute(query)

        users = result.scalars().all()

    success = 0

    for user in users:

        try:

            await bot.send_message(
                chat_id=user.telegram_id,
                text=message.text
            )

            success += 1

        except Exception:
            pass

    await message.answer(
        f"✅ Рассылка завершена\n\n"
        f"📨 Отправлено: {success}"
    )

    await state.clear()

    await log_action(
        user_id=message.from_user.id,

        action="BROADCAST",

        text=message.text
    )