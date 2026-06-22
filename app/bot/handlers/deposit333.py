from aiogram import Bot
from aiogram import Router, F

from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import asyncio

from app.bot.states.deposit import AddDeposit

from app.bot.states.admin import Broadcast

from app.utils.is_admin import is_admin

from aiogram.filters import StateFilter

from app.bot.keyboards.admin import (
    admin_keyboard
)

from app.utils.db_logger import (
    log_action
)

from app.utils.logger import (
    logger
)

from app.bot.keyboards.deposit_card import (
    deposit_card_keyboard
)

from app.database.database import async_session
from app.database.models.deposit import Deposit

from decimal import (
    Decimal,
    InvalidOperation
)

from app.bot.keyboards.wizard import (
    wizard_keyboard
)

from sqlalchemy import select
from sqlalchemy import delete

from datetime import (
    timedelta,
    datetime
)

from dateutil.relativedelta import (
    relativedelta
)

from aiogram.types import CallbackQuery

from sqlalchemy import update



from app.database.models.user import User

from app.bot.states.edit import (
    EditDeposit
)

from aiogram_calendar import (
    SimpleCalendar,
    SimpleCalendarCallback
)

from app.bot.keyboards.settings import (
    settings_keyboard
)

from app.bot.keyboards.sort import (
    sort_keyboard
)

from app.bot.keyboards.banks import (
    banks_keyboard
)

from app.bot.keyboards.open_date import (
    open_date_keyboard
)

from app.bot.keyboards.edit_keyboard import (
    edit_keyboard
)

from app.bot.keyboards.delete_keyboard import (
    delete_keyboard
)

from app.bot.keyboards.deposit_card import (
    deposit_card_keyboard
)

from app.bot.keyboards.capitalization import (
    capitalization_keyboard
)

from app.bot.keyboards.delete_confirm import (
    delete_confirm_keyboard
)

from app.utils.is_admin import (
    is_admin
)

from app.config.config import (
    ADMINS
)

from app.bot.keyboards.admin import (
    admin_keyboard
)

from app.bot.keyboards.cancel import (
    cancel_keyboard
)

from aiogram import (
    Router,
    F
)

from app.bot.keyboards.menu import (
    main_keyboard
)

router = Router()

@router.message(F.text == "❌ Отмена")
async def cancel_handler(
        message: Message,
        state: FSMContext
):
    current_state = await state.get_state()

    if current_state is None:
        return

    await state.clear()

    await message.answer(
        "❌ Создание вклада отменено",
        reply_markup=main_keyboard
    )


async def send_deposit_card(
        message: Message,
        deposit: Deposit
):
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

        total = deposit.amount + profit

    total_days = (
        end_date - deposit.created_at
    ).days

    passed_days = (
        datetime.utcnow() - deposit.created_at
    ).days

    if passed_days < 0:
        passed_days = 0

    days_left = total_days - passed_days

    if days_left < 0:
        days_left = 0

    progress_percent = int(
        (passed_days / total_days) * 100
    ) if total_days > 0 else 0

    filled = int(progress_percent / 10)

    progress_bar = (
        "█" * filled
        + "░" * (10 - filled)
    )

    text = (
        f"🏦 <b>{deposit.bank}</b>\n"

        f"📄 <b>{deposit.deposit_name}</b>\n\n"

        f"💰 Вклад: "
        f"<b>{deposit.amount:,.2f} ₽</b>\n"

        f"📈 Ставка: "
        f"<b>{deposit.rate}%</b>\n"

        f"⏳ Срок: "
        f"<b>{deposit.months} мес.</b>\n\n"

        f"💵 Прибыль: "
        f"<b>{profit:,.2f} ₽</b>\n\n"

        f"🏁 Итог: "
        f"<b>{total:,.2f} ₽</b>\n"

        f"📅 Закроется: "
        f"<b>{end_date.strftime('%d.%m.%Y')}</b>"

        f"\n\n"

        f"⏳ Осталось: "
        f"<b>{days_left} дн.</b>\n"

        f"📊 Прогресс: "
        f"{progress_bar} "
        f"<b>{progress_percent}%</b>"
    )

    await message.answer(
        text,

        reply_markup=deposit_card_keyboard(
            deposit.id
        )
    )


@router.message(F.text == "➕ Добавить вклад")
async def add_button(
        message: Message,
        state: FSMContext
):
    await state.set_state(AddDeposit.bank)

    msg = await message.answer(

        "➕ <b>Добавление вклада</b>\n\n"

        "Шаг 1/6\n\n"

        "🏦 Выберите банк:",

        reply_markup=banks_keyboard
    )

    await state.update_data(
        wizard_message_id=msg.message_id,
        wizard_chat_id=msg.chat.id
    )

    await state.update_data(
        wizard_chat_id=msg.chat.id
    )

@router.message(Command("add"))
async def add_deposit_start(
        message: Message,
        state: FSMContext
):
    await state.set_state(AddDeposit.bank)

    await message.answer(
        "Выберите банк:",
        reply_markup=banks_keyboard
    )


@router.message(
    StateFilter(AddDeposit.bank)
)
async def add_bank(
        message: Message,
        state: FSMContext
):
    data = await state.get_data()

    await message.bot.edit_message_text(

        chat_id=message.chat.id,

        message_id=data[
            "wizard_message_id"
        ],

        text=(

            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 2/6\n\n"

            "📄 Введите название вклада:"
        ),

        reply_markup=wizard_keyboard(
            "bank"
        )
    )

    await state.update_data(
        bank=message.text
    )

    await state.set_state(
        AddDeposit.deposit_name
    )

    await asyncio.sleep(0.3)

    try:

        await message.delete()

    except Exception as e:
        print(e)


@router.message(
    StateFilter(AddDeposit.deposit_name)
)
async def add_deposit_name(
        message: Message,
        state: FSMContext
):
    data = await state.get_data()

    try:

        bot = message.bot

        asyncio.create_task(

            bot.edit_message_text(

                chat_id=message.chat.id,

                message_id=data[
                    "wizard_message_id"
                ],

                parse_mode="HTML",

                text=(

                    "➕ <b>Добавление вклада</b>\n\n"

                    "Шаг 3/6\n\n"

                    "💰 Введите сумму вклада:"
                ),

                reply_markup=wizard_keyboard(
                    "deposit_name"
                )
            )

        )

    except Exception as e:

        print(
            "EDIT ERROR:",
            e
        )

    await state.update_data(
        deposit_name=message.text
    )

    await state.set_state(
        AddDeposit.amount
    )

    try:
        print("ss")
        await message.delete()

    except Exception as e:
        print(e)


@router.message(AddDeposit.amount)
async def add_amount(
        message: Message,
        state: FSMContext
):
    try:
        amount = Decimal(
            message.text.replace(
                " ", ""
            ).replace(",", ".")
        )

    except:
        return await message.answer(
            "❌ Введите корректную сумму"
        )

    data = await state.get_data()

    print(data)

    await message.bot.edit_message_text(

        chat_id=message.chat.id,

        message_id=data[
            "wizard_message_id"
        ],

        text=(
            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 4/6\n\n"

            "📈 Введите процентную ставку:"
        ),

        reply_markup=wizard_keyboard(
            "amount"
        )
    )

    await state.update_data(
        amount=amount
    )

    await state.set_state(
        AddDeposit.rate
    )

    try:

        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:
        print(e)


@router.message(AddDeposit.rate)
async def add_rate(
        message: Message,
        state: FSMContext
):
    try:
        rate = Decimal(
            message.text.replace(
                ",", "."
            )
        )

    except:
        return await message.answer(
            "❌ Введите корректную ставку"
        )

    data = await state.get_data()

    print(data)

    await message.bot.edit_message_text(

        chat_id=message.chat.id,

        message_id=data[
            "wizard_message_id"
        ],

        text=(
            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 5/6\n\n"

            "⏳ Введите срок вклада:"
        ),

        reply_markup=wizard_keyboard(
            "rate"
        )
    )

    try:

        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:
        print(e)

    await state.update_data(
        rate=rate
    )

    await state.set_state(
        AddDeposit.months
    )


@router.message(AddDeposit.months)
async def add_months(
        message: Message,
        state: FSMContext
):
    try:
        months = int(message.text)

    except:
        return await message.answer(
            "❌ Введите срок числом"
        )

    data = await state.get_data()

    print(data)

    await message.bot.edit_message_text(

        chat_id=message.chat.id,

        message_id=data[
            "wizard_message_id"
        ],

        text=(
            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 6/6\n\n"

            "📅 Когда открыт вклад?"
        ),

        reply_markup=open_date_keyboard
    )

    try:

        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:
        print(e)

    await state.update_data(
        months=months
    )

    await state.set_state(
        AddDeposit.choose_open_date
    )




@router.message(F.text == "📋 Мои вклады")
async def deposits_button(message: Message):
    await get_deposits(message)


@router.message(Command("list"))
async def get_deposits(message: Message):

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

    for deposit in deposits:

        await send_deposit_card(
            message,
            deposit
        )


@router.message(F.text == "❌ Удалить вклад")
async def delete_menu(message: Message):

    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == message.from_user.id
        )

        result = await session.execute(query)

        deposits = result.scalars().all()

    if not deposits:

        await message.answer(
            "У вас нет вкладов"
        )

        return

    await message.answer(
        "Выберите вклад для удаления:",
        reply_markup=delete_keyboard(deposits)
    )


@router.callback_query(
    F.data.startswith("delete_")
)
async def delete_deposit_menu(
        callback: CallbackQuery
):
    deposit_id = int(
        callback.data.split("_")[1]
    )

    await callback.message.edit_text(
        "❗ Вы уверены что хотите удалить вклад?",
        reply_markup=delete_confirm_keyboard(
            deposit_id
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("confirm_delete_")
)
async def confirm_delete(
        callback: CallbackQuery
):
    deposit_id = int(
        callback.data.split("_")[2]
    )

    async with async_session() as session:

        query = delete(Deposit).where(
            Deposit.id == deposit_id
        )

        await session.execute(query)

        await log_action(
            user_id=callback.from_user.id,

            action="DELETE_DEPOSIT",

            text=f"deposit_id={deposit_id}"
        )

        await session.commit()

    await callback.message.edit_text(
        "✅ Вклад удален"
    )

    await callback.answer()


@router.callback_query(
    F.data == "cancel_delete"
)
async def cancel_delete(
        callback: CallbackQuery
):
    await callback.message.edit_text(
        "❌ Удаление отменено"
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("info_")
)
async def deposit_info(
        callback: CallbackQuery
):
    deposit_id = int(
        callback.data.split("_")[-1]
    )

    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.id == deposit_id
        )

        result = await session.execute(query)

        deposit = result.scalar()

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

        total = deposit.amount + profit

    start_date = deposit.created_at

    total_days = (
        end_date - start_date
    ).days

    passed_days = (
        datetime.utcnow() - start_date
    ).days

    if passed_days < 0:
        passed_days = 0

    days_left = total_days - passed_days

    if days_left < 0:
        days_left = 0

    progress_percent = int(
        (passed_days / total_days) * 100
    ) if total_days > 0 else 0

    filled = int(progress_percent / 10)

    progress_bar = (
        "█" * filled
        + "░" * (10 - filled)
    )

    monthly_profit = (
        profit / Decimal(deposit.months)
    )

    payments_text = ""

    received_profit = Decimal("0")

    future_text = ""

    next_payment = None

    for month in range(deposit.months):

        payment_date = (
            deposit.created_at
            + relativedelta(
                months=month + 1
            )
        )

        payment_amount = monthly_profit

        payment_line = (
            f"{payment_date.strftime('%d.%m.%Y')} "
            f"— "
            f"+{payment_amount:,.2f} ₽"
        )

        if payment_date <= datetime.utcnow():

            payments_text += (
                payment_line + "\n"
            )

            received_profit += (
                payment_amount
            )

        else:

            future_text += (
                payment_line + "\n"
            )

            if not next_payment:

                next_payment = payment_date

    forecast = (
        profit - received_profit
    )

    text = (
        f"🏦 <b>{deposit.bank}</b>\n\n"

        f"📄 {deposit.deposit_name}\n\n"

        f"💰 Вклад:\n"
        f"{deposit.amount:,.2f} ₽\n\n"

        f"📈 Ставка:\n"
        f"{deposit.rate}%\n\n"

        f"⏳ Срок:\n"
        f"{deposit.months} мес.\n\n"

        f"💵 Прибыль:\n"
        f"{profit:,.2f} ₽\n\n"

        f"🏁 Итоговая сумма:\n"
        f"{total:,.2f} ₽\n\n"

        f"📅 Дата окончания:\n"
        f"{end_date.strftime('%d.%m.%Y')}\n\n"

        f"⏳ Осталось:\n"
        f"{days_left} дн.\n\n"

        f"📊 Прогресс:\n"
        f"{progress_bar} "
        f"{progress_percent}%"
    )

    if payments_text:

        text += (
            f"\n\n💸 Выплаты по месяцам:\n\n"

            f"{payments_text}"
        )

    if received_profit > 0:

        text += (
            f"\n✅ Получено:\n"
            f"{received_profit:,.2f} ₽"
        )

    if next_payment:

        text += (
            f"\n\n💸 Ближайшая выплата:\n"
            f"{next_payment.strftime('%d.%m.%Y')}"
        )

    if future_text:

        text += (
            f"\n\n📅 Следующие выплаты:\n\n"

            f"{future_text}"
        )

    text += (
        f"\n📈 Прогноз до конца:\n"
        f"{forecast:,.2f} ₽"
    )

    await callback.answer()

    await callback.message.edit_text(
        text,

        reply_markup=deposit_card_keyboard(
            deposit.id,
            details=True
        )
    )


@router.callback_query(
    AddDeposit.capitalization,
    F.data.in_(["cap_yes", "cap_no"])
)
async def capitalization_handler(
        callback: CallbackQuery,
        state: FSMContext
):
    capitalization = (
        callback.data == "cap_yes"
    )

    await state.update_data(
        capitalization=capitalization
    )

    data = await state.get_data()

    async with async_session() as session:

        deposit = Deposit(
            user_id=callback.from_user.id,
            bank=data["bank"],
            deposit_name=data["deposit_name"],
            amount=data["amount"],
            rate=data["rate"],
            months=data["months"],
            created_at=data["created_at"],
            capitalization=data["capitalization"]
        )

        session.add(deposit)

        await session.commit()

        await log_action(
            user_id=callback.from_user.id,

            action="ADD_DEPOSIT",

            text=(
                f"{data['bank']} | "
                f"{data['amount']} ₽ | "
                f"{data['rate']}%"
            )
        )

    await callback.message.edit_text(

        "✅ <b>Вклад успешно добавлен</b>\n\n"

        "🎉 Все данные сохранены",
        reply_markup=main_keyboard
    )

    await callback.answer()

    await state.clear()



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

    await message.answer(text)


@router.callback_query(
    F.data.startswith("deposit_edit_")
)
async def edit_menu(
        callback: CallbackQuery,
        state: FSMContext
):
    deposit_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        deposit_id=deposit_id
    )

    await callback.message.edit_text(
        "Что хотите изменить?",

        reply_markup=edit_keyboard(
            deposit_id
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("edit_amount_")
)
async def edit_amount_start(
        callback: CallbackQuery,
        state: FSMContext
):
    deposit_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        deposit_id=deposit_id
    )

    await state.set_state(
        EditDeposit.amount
    )

    await callback.message.answer(
        "💰 Введите новую сумму",

        reply_markup=cancel_keyboard
    )

    await callback.answer()


@router.message(EditDeposit.amount)
async def edit_amount_finish(
        message: Message,
        state: FSMContext
):
    try:
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:
        print(e)

    try:
        amount_text = (
            message.text
            .replace(",", ".")
            .replace(" ", "")
        )

        amount = Decimal(amount_text)

        if amount <= 0:

            await message.answer(
                "❌ Сумма должна быть больше 0"
            )

            return

    except (
            ValueError,
            InvalidOperation
    ):

        await message.answer(
            "❌ Некорректная сумма\n\n"
            "Введите число"
            "Например: 500000"
        )

        return

    data = await state.get_data()

    async with async_session() as session:

        query = (
            update(Deposit)
            .where(
                Deposit.id == data["deposit_id"]
            )
            .values(amount=amount)
        )

        await session.execute(query)

        await session.commit()

        logger.info(

            f"EDIT AMOUNT | "

            f"user={message.from_user.id} | "

            f"deposit_id={data['deposit_id']} | "

            f"new_amount={amount}"
        )

        query = select(Deposit).where(
            Deposit.id == data["deposit_id"]
        )

        result = await session.execute(query)

        deposit = result.scalar()

    await message.answer(
        "✅ Сумма обновлена"
    )

    await send_deposit_card(
        message,
        deposit
    )

    await state.clear()



@router.callback_query(
    F.data.startswith("edit_rate_")
)
async def edit_rate_start(
        callback: CallbackQuery,
        state: FSMContext
):
    deposit_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        deposit_id=deposit_id
    )

    await state.set_state(
        EditDeposit.rate
    )

    await callback.message.answer(
        "Введите новую ставку:",
        reply_markup = cancel_keyboard
    )

    await callback.answer()


@router.message(EditDeposit.rate)
async def edit_rate_finish(
        message: Message,
        state: FSMContext
):
    try:
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:
        print(e)

    try:
        rate_text = (
            message.text
            .replace(",", ".")
            .replace(" ", "")
        )

        rate = Decimal(rate_text)

        if rate <= 0:

            await message.answer(
                "❌ Ставка должна быть больше 0"
            )

            return

    except (
            ValueError,
            InvalidOperation
    ):

        await message.answer(
            "❌ Некорректная ставка\n\n"
            "Введите число"
            "Например: 15"
        )

        return

    data = await state.get_data()

    async with async_session() as session:

        query = (
            update(Deposit)
            .where(
                Deposit.id == data["deposit_id"]
            )
            .values(rate=rate)
        )

        await session.execute(query)

        await session.commit()

        logger.info(

            f"EDIT AMOUNT | "

            f"user={message.from_user.id} | "

            f"deposit_id={data['deposit_id']} | "

            f"new_rate={rate}"
        )

        query = select(Deposit).where(
            Deposit.id == data["deposit_id"]
        )

        result = await session.execute(query)

        deposit = result.scalar()

    await message.answer(
        "✅ Ставка обновлена"
    )

    await send_deposit_card(
        message,
        deposit
    )

    await state.clear()


@router.callback_query(
    F.data.startswith("edit_months_")
)
async def edit_months_start(
        callback: CallbackQuery,
        state: FSMContext
):
    deposit_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        deposit_id=deposit_id
    )

    await state.set_state(
        EditDeposit.months
    )

    await callback.message.answer(
        "Введите новый срок:",
        reply_markup=main_keyboard
    )

    await callback.answer()


@router.message(EditDeposit.months)
async def edit_months_finish(
        message: Message,
        state: FSMContext
):
    try:
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:
        print(e)

    try:

        months = int(message.text)

        if months <= 0:
            await message.answer(
                "❌ Срок должен быть больше 0"
            )

            return

    except Exception:

        await message.answer(
            "❌ Введите целое число"
        )

        return

    data = await state.get_data()

    async with async_session() as session:

        query = (
            update(Deposit)
            .where(
                Deposit.id == data["deposit_id"]
            )
            .values(months=months)
        )

        await session.execute(query)

        await session.commit()

        logger.info(

            f"EDIT AMOUNT | "

            f"user={message.from_user.id} | "

            f"deposit_id={data['deposit_id']} | "

            f"new_months={months}"
        )

        query = select(Deposit).where(
            Deposit.id == data["deposit_id"]
        )

        result = await session.execute(query)

        deposit = result.scalar()

    await message.answer(
        "✅ Срок обновлен"
    )

    await send_deposit_card(
        message,
        deposit
    )

    await state.clear()



@router.message(F.text == "⚙ Настройки")
async def settings_handler(
        message: Message
):
    await log_action(
        user_id=message.from_user.id,

        action="OPEN_SETTINGS"
    )

    async with async_session() as session:

        query = select(User).where(
            User.telegram_id
            == message.from_user.id
        )

        result = await session.execute(query)

        user = result.scalar()

    status = (
        "ВКЛ"
        if user.notifications_enabled
        else
        "ВЫКЛ"
    )

    await message.answer(
        f"⚙ <b>Настройки</b>\n\n"

        f"🔔 Уведомления: "
        f"<b>{status}</b>\n\n"

        f"🌍 Часовой пояс:\n"
        f"<b>{user.timezone}</b>\n\n"

        f"⏰ Время уведомлений:\n"
        f"<b>{user.notification_hour}:00</b>",

        reply_markup=settings_keyboard(
            user.notifications_enabled
        )
    )


@router.callback_query(
    F.data == "toggle_notifications"
)
async def toggle_notifications(
        callback: CallbackQuery
):
    async with async_session() as session:

        query = select(User).where(
            User.telegram_id
            == callback.from_user.id
        )

        result = await session.execute(query)

        user = result.scalar()

        user.notifications_enabled = (
            not user.notifications_enabled
        )

        enabled = user.notifications_enabled

        await session.commit()

        await log_action(
            user_id=callback.from_user.id,

            action="TOGGLE_NOTIFICATIONS",

            text=f"enabled={enabled}"
        )

        status = (
            "ВКЛ"
            if enabled
            else "ВЫКЛ"
        )

    await callback.message.edit_text(
        f"⚙ <b>Настройки</b>\n\n"
        f"🔔 Уведомления: "
        f"<b>{status}</b>",

        reply_markup=settings_keyboard(
            enabled
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("bank_")
)
async def choose_bank(
        callback: CallbackQuery,
        state: FSMContext
):
    bank = callback.data.replace(
        "bank_",
        ""
    )

    await callback.answer()


    if bank == "custom":

        await state.set_state(
            AddDeposit.bank
        )

        await callback.message.edit_text(

            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 1/6\n\n"

            "🏦 Введите название банка:",

            reply_markup=wizard_keyboard(
                "bank"
            )
        )

        return

    await state.update_data(
        bank=bank
    )

    await state.set_state(
        AddDeposit.deposit_name
    )

    await callback.message.edit_text(

        "➕ <b>Добавление вклада</b>\n\n"

        "Шаг 2/6\n\n"

        "📄 Введите название вклада:",

        reply_markup=wizard_keyboard(
            "bank"
        )
    )





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

        end_date = (
                deposit.created_at
                + relativedelta(
            months=deposit.months
        )
        )

        days_left = (
            end_date - datetime.utcnow()
        ).days

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



@router.callback_query(
    F.data == "date_today"
)
async def today_open_date(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.update_data(
        created_at=datetime.utcnow()
    )

    await state.set_state(
        AddDeposit.capitalization
    )

    await callback.message.answer(
        "Есть капитализация процентов?",
        reply_markup=capitalization_keyboard
    )

    await callback.answer()



@router.callback_query(
    F.data == "deposit_custom_date"
)
async def custom_open_date(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.set_state(
        AddDeposit.choose_open_date
    )

    await callback.message.edit_text(
        "📅 Выберите дату:",
        reply_markup=await SimpleCalendar().start_calendar()
    )

    await callback.answer()




@router.callback_query(
    SimpleCalendarCallback.filter()
)
async def process_simple_calendar(
        callback: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    selected, date = await SimpleCalendar().process_selection(
        callback,
        callback_data
    )

    if not selected:
        return

    if date.date() > datetime.utcnow().date():
        await callback.message.edit_text(
            "❌ Дата не может быть в будущем\n\n"
            "📅 Выберите корректную дату:",
            reply_markup=await SimpleCalendar().start_calendar()
        )

        return

    await state.update_data(
        created_at=date
    )

    await state.set_state(
        AddDeposit.capitalization
    )

    await callback.message.edit_text(
        "Есть капитализация процентов?",
        reply_markup=capitalization_keyboard
    )



@router.callback_query(
    F.data == "cancel_add_deposit"
)
async def cancel_add_deposit(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.clear()

    await callback.message.edit_text(
        "❌ Создание вклада отменено"
    )

    await callback.message.answer(
        "Главное меню",
        reply_markup=main_keyboard
    )

    await callback.answer()



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


@router.callback_query(
    F.data.startswith("edit_name_")
)
async def edit_name_start(
        callback: CallbackQuery,
        state: FSMContext
):
    deposit_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        deposit_id=deposit_id
    )

    await state.set_state(
        EditDeposit.edit_name
    )

    await callback.message.answer(
        "📄 Введите новое название вклада",
        reply_markup=main_keyboard
    )

    await callback.answer()


@router.message(
    EditDeposit.edit_name
)
async def edit_name_finish(
        message: Message,
        state: FSMContext
):
    try:
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:
        print(e)

    data = await state.get_data()

    deposit_id = data["deposit_id"]

    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.id == deposit_id
        )

        result = await session.execute(query)

        deposit = result.scalar()

        deposit.deposit_name = (
            message.text
        )

        await session.commit()

        await log_action(
            user_id=message.from_user.id,

            action="EDIT_NAME",

            text=message.text
        )

    await message.answer(
        "✅ Название обновлено"
    )

    await state.clear()



@router.callback_query(
    F.data.startswith("edit_date_")
)
async def edit_date_start(
        callback: CallbackQuery,
        state: FSMContext
):
    deposit_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        deposit_id=deposit_id
    )

    await state.set_state(
        EditDeposit.edit_date
    )

    await callback.message.answer(
        "📅 Введите новую дату\n\n"
        "Пример: 25.05.2025",
        reply_markup=main_keyboard
    )

    await callback.answer()



@router.message(
    EditDeposit.edit_date
)
async def edit_date_finish(
        message: Message,
        state: FSMContext
):
    try:
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:
        print(e)

    try:

        new_date = datetime.strptime(
            message.text,
            "%d.%m.%Y"
        )

    except ValueError:

        await message.answer(
            "❌ Неверный формат даты\n\n"
            "Пример: 25.05.2025"
        )

        return

    if new_date.date() > datetime.utcnow().date():

        await message.answer(
            "❌ Дата не может быть "
            "в будущем"
        )

        return

    data = await state.get_data()

    deposit_id = data["deposit_id"]

    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.id == deposit_id
        )

        result = await session.execute(query)

        deposit = result.scalar()

        deposit.created_at = new_date

        await session.commit()

        await log_action(
            user_id=message.from_user.id,

            action="EDIT_DATE",

            text=str(new_date)
        )

    await message.answer(
        "✅ Дата обновлена"
    )

    await state.clear()



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

        query = select(Deposit).where(
            Deposit.id == deposit_id
        )

        result = await session.execute(query)

        deposit = result.scalar()

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

        total = deposit.amount + profit

    total_days = (
        end_date - deposit.created_at
    ).days

    passed_days = (
        datetime.utcnow() - deposit.created_at
    ).days

    if passed_days < 0:
        passed_days = 0

    days_left = total_days - passed_days

    if days_left < 0:
        days_left = 0

    progress_percent = int(
        (passed_days / total_days) * 100
    ) if total_days > 0 else 0

    filled = int(progress_percent / 10)

    progress_bar = (
        "█" * filled
        + "░" * (10 - filled)
    )

    text = (
        f"🏦 <b>{deposit.bank}</b>\n"

        f"📄 <b>{deposit.deposit_name}</b>\n\n"

        f"💰 Вклад: "
        f"<b>{deposit.amount:,.2f} ₽</b>\n"

        f"📈 Ставка: "
        f"<b>{deposit.rate}%</b>\n"

        f"⏳ Срок: "
        f"<b>{deposit.months} мес.</b>\n\n"

        f"💵 Прибыль: "
        f"<b>{profit:,.2f} ₽</b>\n\n"

        f"🏁 Итог: "
        f"<b>{total:,.2f} ₽</b>\n"

        f"📅 Закроется: "
        f"<b>{end_date.strftime('%d.%m.%Y')}</b>"

        f"\n\n"

        f"⏳ Осталось: "
        f"<b>{days_left} дн.</b>\n"

        f"📊 Прогресс: "
        f"{progress_bar} "
        f"<b>{progress_percent}%</b>"
    )

    await callback.message.edit_text(
        text,

        reply_markup=deposit_card_keyboard(
            deposit.id
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
    F.data.startswith("wizard_back_")
)
async def wizard_back(
        callback: CallbackQuery,
        state: FSMContext
):
    step = callback.data.split("_")[-1]

    if step == "bank":

        await state.set_state(
            AddDeposit.bank
        )

        await callback.message.edit_text(

            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 1/6\n\n"

            "🏦 Выберите банк:",

            reply_markup=banks_keyboard
        )

    elif step == "deposit_name":

        await state.set_state(
            AddDeposit.deposit_name
        )

        await callback.message.edit_text(

            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 2/6\n\n"

            "📄 Введите название вклада:",

            reply_markup=wizard_keyboard(
                "bank"
            )
        )

    elif step == "amount":

        await state.set_state(
            AddDeposit.amount
        )

        await callback.message.edit_text(

            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 3/6\n\n"

            "💰 Введите сумму вклада:",

            reply_markup=wizard_keyboard(
                "deposit_name"
            )
        )

    elif step == "rate":

        await state.set_state(
            AddDeposit.rate
        )

        await callback.message.edit_text(

            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 4/6\n\n"

            "📈 Введите процентную ставку:",

            reply_markup=wizard_keyboard(
                "amount"
            )
        )

    elif step == "months":

        await state.set_state(
            AddDeposit.months
        )

        await callback.message.edit_text(

            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 5/6\n\n"

            "⏳ Введите срок вклада:",

            reply_markup=wizard_keyboard(
                "rate"
            )
        )

    await callback.answer()


@router.message()
async def all_messages_logger(
        message: Message
):
    await log_action(
        user_id=message.from_user.id,

        action="MESSAGE",

        text=message.text
    )
