from app.core.imports import *

from .cards import (
    send_deposit_card
)

from app.services.deposit_calculator import (
    calculate_deposit_stats
)

router = Router()

@router.message(F.text == "📊 Аналитика")
async def analytics_handler(
        message: Message
):
    await log_action(
        user_id=message.from_user.id,

        action="OPEN_ANALYTICS"
    )

    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == message.from_user.id
        )

        result = await session.execute(query)

        deposits = result.scalars().all()

    if not deposits:

        await message.answer(
            "У вас пока нет вкладов"
        )

        return

    total_amount = Decimal("0")
    total_profit = Decimal("0")
    total_rate = Decimal("0")

    monthly_stats = {}

    banks_stats = {}

    banks_profit = {}

    yearly_stats = {}

    bank_yearly_stats = {}

    months_ru = {
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь"
    }

    for deposit in deposits:

        if deposit.product_type == "savings":

            total_amount += deposit.amount
            total_rate += deposit.rate

            profit = (
                    deposit.amount
                    * deposit.rate
                    / Decimal("100")
            )

            total_profit += profit

            if deposit.bank not in banks_stats:
                banks_stats[deposit.bank] = 0

            banks_stats[deposit.bank] += 1

            if deposit.bank not in banks_profit:
                banks_profit[deposit.bank] = Decimal("0")

            banks_profit[deposit.bank] += profit

            continue

        total_amount += deposit.amount
        total_rate += deposit.rate

        if deposit.bank not in banks_stats:

            banks_stats[
                deposit.bank
            ] = 0

        banks_stats[
            deposit.bank
        ] += 1

        end_date = (
            deposit.created_at
            + relativedelta(
                months=deposit.months
            )
        )

        days = (
            end_date - deposit.created_at
        ).days

        if deposit.capitalization:

            total = deposit.amount * (
                (
                    Decimal("1")
                    + (
                        deposit.rate
                        / Decimal("100")
                        / Decimal("12")
                    )
                ) ** deposit.months
            )

            profit = total - deposit.amount

        else:

            profit = (
                deposit.amount *
                (deposit.rate / Decimal("100")) *
                Decimal(days)
                / Decimal("365")
            )

            monthly_profit = (
                profit / Decimal(deposit.months)
            )

            for month in range(deposit.months):

                payment_date = (
                    deposit.created_at
                    + relativedelta(
                        months=month + 1
                    )
                )

                year = payment_date.strftime(
                    "%Y"
                )

                month_name = months_ru[
                    payment_date.month
                ]

                full_key = (
                    f"{year} — {month_name}"
                )

                if full_key not in monthly_stats:

                    monthly_stats[
                        full_key
                    ] = Decimal("0")

                monthly_stats[
                    full_key
                ] += monthly_profit

                if year not in yearly_stats:
                    yearly_stats[
                        year
                    ] = Decimal("0")

                yearly_stats[
                    year
                ] += monthly_profit

                if deposit.bank not in bank_yearly_stats:
                    bank_yearly_stats[
                        deposit.bank
                    ] = {}

                if year not in bank_yearly_stats[
                    deposit.bank
                ]:
                    bank_yearly_stats[
                        deposit.bank
                    ][year] = Decimal("0")

                bank_yearly_stats[
                    deposit.bank
                ][year] += monthly_profit

        total_profit += profit

        if deposit.bank not in banks_profit:

            banks_profit[
                deposit.bank
            ] = Decimal("0")

        banks_profit[
            deposit.bank
        ] += profit

    average_rate = (
        total_rate / Decimal(len(deposits))
    )

    monthly_text = ""

    for month, value in sorted(
        monthly_stats.items()
    ):

        monthly_text += (
            f"{month} — "
            f"{value:,.2f} ₽\n"
        )

    banks_text = ""

    for bank, count in sorted(
        banks_stats.items()
    ):

        banks_text += (
            f"{bank} — "
            f"{count}\n"
        )

    profit_by_bank_text = ""

    yearly_text = ""

    for year, value in sorted(
            yearly_stats.items()
    ):
        yearly_text += (
            f"{year} — "
            f"{value:,.2f} ₽\n"
        )

    bank_yearly_text = ""

    for bank, years in sorted(
            bank_yearly_stats.items()
    ):

        bank_yearly_text += (
            f"\n🏦 {bank}\n"
        )

        for year, value in sorted(
                years.items()
        ):
            bank_yearly_text += (
                f"{year} — "
                f"{value:,.2f} ₽\n"
            )

    for bank, value in sorted(
        banks_profit.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        profit_by_bank_text += (
            f"{bank} — "
            f"{value:,.2f} ₽\n"
        )

    text = (
        f"📊 <b>Аналитика портфеля</b>\n\n"

        f"💼 Всего вложено:\n"
        f"<b>{total_amount:,.2f} ₽</b>\n\n"

        f"💵 Общая прибыль:\n"
        f"<b>{total_profit:,.2f} ₽</b>\n\n"

        f"🏦 Количество вкладов:\n"
        f"<b>{len(deposits)}</b>\n\n"

        f"📈 Средняя ставка:\n"
        f"<b>{average_rate:.2f}%</b>\n\n"

        f"🏦 Банки:\n\n"

        f"{banks_text}\n"

        f"💵 Прибыль по банкам:\n\n"

        f"{profit_by_bank_text}"
    )

    if monthly_text:

        text += (
            f"\n━━━━━━━━━━━━━━\n\n"

            f"📅 Прибыль по месяцам\n\n"

            f"{monthly_text}"
        )

    if yearly_text:
        text += (
            f"\n━━━━━━━━━━━━━━\n\n"
            f"📊 Прибыль по годам\n\n"
            f"{yearly_text}"
        )

    if bank_yearly_text:
        text += (
            f"\n━━━━━━━━━━━━━━\n\n"
            f"🏦 Прибыль по банкам и годам\n"
            f"{bank_yearly_text}"
        )

    await message.answer(text)


@router.message(
    F.text == "🔥 Скоро"
)
async def ending_soon_handler(
        message: Message
):
    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == message.from_user.id
        )

        result = await session.execute(query)

        deposits = result.scalars().all()

    ending_deposits = []

    for deposit in deposits:

        if deposit.product_type == "savings":
            continue

        stats = calculate_deposit_stats(
            deposit
        )

        end_date = stats["end_date"]
        days_left = stats["days_left"]

        if 0 <= days_left <= 30:

            ending_deposits.append(
                (
                    deposit,
                    days_left,
                    end_date
                )
            )

    if not ending_deposits:

        await message.answer(
            "✅ Нет вкладов, которые скоро заканчиваются"
        )

        return

    for deposit, days_left, end_date in ending_deposits:

        text = (
            f"🏦 <b>{deposit.bank}</b>\n"

            f"📄 <b>{deposit.deposit_name}</b>\n\n"

            f"⏳ Осталось:\n"
            f"<b>{days_left} дн.</b>\n\n"

            f"📅 Закрытие:\n"
            f"<b>{end_date.strftime('%d.%m.%Y')}</b>"
        )

        await message.answer(text)



@router.message(
    F.text == "📂 Сортировка"
)
async def sort_menu(
        message: Message
):
    await message.answer(
        "Выберите сортировку:",
        reply_markup=sort_keyboard
    )



@router.callback_query(
    F.data.startswith("sort_")
)
async def sort_deposits(
        callback: CallbackQuery
):
    sort_type = callback.data.split("_")[1]

    await log_action(
        user_id=callback.from_user.id,

        action="SORT_DEPOSITS",

        text=sort_type
    )

    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == callback.from_user.id
        )

        result = await session.execute(query)

        deposits = result.scalars().all()

    if sort_type == "amount":

        deposits.sort(
            key=lambda x: x.amount,
            reverse=True
        )

    elif sort_type == "rate":

        deposits.sort(
            key=lambda x: x.rate,
            reverse=True
        )

    elif sort_type == "months":

        deposits.sort(
            key=lambda x: x.months,
            reverse=True
        )

    await callback.message.answer(
        "📂 Отсортированные вклады:"
    )

    for deposit in deposits:

        await send_deposit_card(
            callback.message,
            deposit
        )

    await callback.answer()