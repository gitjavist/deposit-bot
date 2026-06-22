from app.core.imports import *

from app.services.deposit_calculator import (
    calculate_deposit_stats
)

from app.bot.keyboards.confirm_close_keyboard import (
    confirm_close_keyboard
)

router = Router()

def render_short_card(deposit: Deposit):
    stats = calculate_deposit_stats(deposit)

    # Накопительный счет
    if deposit.product_type == "savings":

        monthly_profit = stats["monthly_profit"]

        return (
            f"💳 <b>{deposit.bank}</b>\n\n"
            f"📂 Накопительный счет\n\n"
            f"📄 <b>{deposit.deposit_name}</b>\n\n"
            f"💰 <b>{deposit.amount:,.2f} ₽</b>\n\n"
            f"📈 <b>{deposit.rate}%</b>\n\n"
            f"📅 Открыт:\n"
            f"<b>{deposit.created_at.strftime('%d.%m.%Y')}</b>\n\n"
            f"💵 В месяц:\n"
            f"<b>{monthly_profit:,.2f} ₽</b>"
        )

    # Вклад
    days_left = stats["days_left"]
    progress_percent = stats["progress_percent"]
    is_closed = stats["is_closed"]
    end_date = stats["end_date"]
    total = stats["total"]

    filled = int(progress_percent / 10)

    progress_bar = (
        "█" * filled +
        "░" * (10 - filled)
    )

    status_text = (
        "✅ Завершен"
        if is_closed
        else "⏳ Активен"
    )

    return (
        f"🏦 <b>{deposit.bank}</b>\n"
        f"📂 Вклад\n\n"
        f"📄 <b>{deposit.deposit_name}</b>\n\n"
        f"📌 {status_text}\n\n"
        f"💰 <b>{deposit.amount:,.2f} ₽</b>\n"
        f"📈 <b>{deposit.rate}%</b>\n"
        f"⏳ <b>{deposit.months} мес.</b>\n\n"
        f"🏁 <b>{total:,.2f} ₽</b>\n"
        f"📅 <b>{end_date.strftime('%d.%m.%Y')}</b>\n\n"
        f"⏳ <b>{days_left} дн.</b>\n\n"
        f"{progress_bar} <b>{progress_percent}%</b>"
    )

async def send_deposit_card(
        message: Message,
        deposit: Deposit
):
    text = render_short_card(
        deposit
    )

    await message.answer(
        text,
        reply_markup=deposit_card_keyboard(
            deposit.id,
            deposit.product_type,
            deposit.is_closed
        )
    )


@router.callback_query(
    F.data.startswith("info_")
)
async def deposit_info(callback: CallbackQuery):
    deposit_id = int(
        callback.data.split("_")[-1]
    )

    async with async_session() as session:

        result = await session.execute(
            select(Deposit).where(Deposit.id == deposit_id)
        )

        deposit = result.scalar()

    # =========================
    # ЕДИНЫЙ РАСЧЁТ
    # =========================
    stats = calculate_deposit_stats(deposit)

    # savings
    if deposit.product_type == "savings":

        monthly_profit = stats["monthly_profit"]

        text = (
            f"💳 <b>{deposit.bank}</b>\n\n"
            f"📂 Накопительный счет\n\n"
            f"📄 <b>{deposit.deposit_name}</b>\n\n"
            f"💰 Остаток:\n"
            f"{deposit.amount:,.2f} ₽\n\n"
            f"📈 Ставка:\n"
            f"{deposit.rate}%\n\n"
            f"📅 Дата открытия:\n"
            f"{deposit.created_at.strftime('%d.%m.%Y')}\n\n"
            f"💵 Доход в месяц:\n"
            f"{monthly_profit:,.2f} ₽\n\n"
        )

        await callback.message.edit_text(
            text,
            reply_markup=deposit_card_keyboard(
                deposit.id,
                details=True
            )
        )

        await callback.answer()
        return

    # =========================
    # DEPOSIT
    # =========================

    end_date = stats["end_date"]
    profit = stats["profit"]
    total = stats["total"]
    days_left = stats["days_left"]
    progress_percent = stats["progress_percent"]
    is_closed = stats["is_closed"]

    filled = int(progress_percent / 10)

    progress_bar = (
        "█" * filled +
        "░" * (10 - filled)
    )

    # =========================
    # МЕСЯЧНЫЕ ВЫПЛАТЫ
    # =========================

    monthly_profit = profit / Decimal(deposit.months)

    payments_text = ""
    future_text = ""
    received_profit = Decimal("0")
    next_payment = None

    for month in range(deposit.months):

        payment_date = deposit.created_at + relativedelta(months=month + 1)
        payment_amount = monthly_profit

        line = (
            f"{payment_date.strftime('%d.%m.%Y')} — "
            f"+{payment_amount:,.2f} ₽"
        )

        if payment_date <= datetime.utcnow():
            payments_text += line + "\n"
            received_profit += payment_amount
        else:
            future_text += line + "\n"
            if not next_payment:
                next_payment = payment_date

    forecast = profit - received_profit

    text = (
        f"🏦 <b>{deposit.bank}</b>\n\n"
        f"📄 {deposit.deposit_name}\n\n"
        f"💰 Вклад:\n{deposit.amount:,.2f} ₽\n\n"
        f"📈 Ставка:\n{deposit.rate}%\n\n"
        f"⏳ Срок:\n{deposit.months} мес.\n\n"
        f"💵 Прибыль:\n{profit:,.2f} ₽\n\n"
        f"🏁 Итоговая сумма:\n{total:,.2f} ₽\n\n"
        f"📅 Дата открытия:\n{deposit.created_at.strftime('%d.%m.%Y')}\n\n"
        f"📅 Дата окончания:\n{end_date.strftime('%d.%m.%Y')}\n\n"
        f"⏳ Осталось:\n{days_left} дн.\n\n"
        f"📊 Прогресс:\n"
        f"{progress_bar} {progress_percent}%"
    )

    if payments_text:
        text += f"\n\n💸 Выплаты по месяцам:\n\n{payments_text}"

    if received_profit > 0:
        text += f"\n\n✅ Получено:\n{received_profit:,.2f} ₽"

    if next_payment:
        text += f"\n\n💸 Ближайшая выплата:\n{next_payment.strftime('%d.%m.%Y')}"

    if future_text:
        text += f"\n\n📅 Следующие выплаты:\n\n{future_text}"

    text += f"\n\n📈 Прогноз до конца:\n{forecast:,.2f} ₽"

    await callback.answer()

    await callback.message.edit_text(
        text,
        reply_markup=deposit_card_keyboard(
            deposit.id,
            details=True
        )
    )


@router.callback_query(
    F.data.startswith("back_")
)
async def back_to_card(
        callback: CallbackQuery
):
    deposit_id = int(
        callback.data.split("_")[-1]
    )

    async with async_session() as session:

        result = await session.execute(
            select(Deposit).where(
                Deposit.id == deposit_id
            )
        )

        deposit = result.scalar()

    text = render_short_card(
        deposit
    )

    await callback.message.edit_text(
        text,
        reply_markup=deposit_card_keyboard(
            deposit.id,
            deposit.product_type,
            deposit.is_closed
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("back_info_")
)
async def back_to_info(
        callback: CallbackQuery
):
    deposit_id = int(
        callback.data.split("_")[2]
    )

    callback.data = f"info_{deposit_id}"

    await deposit_info(callback)


@router.callback_query(
    F.data.startswith("close_")
)
async def close_account(
        callback: CallbackQuery
):
    deposit_id = int(
        callback.data.split("_")[-1]
    )

    await callback.message.edit_text(
        "⚠️ Закрыть накопительный счёт?",
        reply_markup=confirm_close_keyboard(
            deposit_id
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("confirm_close_")
)
async def confirm_close_account(
        callback: CallbackQuery
):
    deposit_id = int(
        callback.data.split("_")[-1]
    )

    async with async_session() as session:

        result = await session.execute(
            select(Deposit).where(
                Deposit.id == deposit_id
            )
        )

        deposit = result.scalar()

        if not deposit:

            await callback.answer(
                "Счёт не найден"
            )

            return

        deposit.is_closed = True

        await session.commit()

    await callback.message.edit_text(
        "✅ Накопительный счёт закрыт"
    )

    await callback.answer()