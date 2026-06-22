from app.core.imports import *

from app.utils.calendar import (
    build_calendar,
    validate_calendar_date
)

from app.bot.keyboards.product_type_keyboard import (
    product_type_keyboard
)

from .cards import (
    send_deposit_card
)

router = Router()

@router.message(F.text == "➕ Добавить вклад")
async def add_button(
        message: Message,
        state: FSMContext
):
    await state.set_state(
        AddDeposit.product_type
    )

    await message.answer(
        "Что хотите добавить?",
        reply_markup=product_type_keyboard
    )

@router.message(Command("add"))
async def add_deposit_start(
        message: Message,
        state: FSMContext
):
    await state.set_state(AddDeposit.product_type)

    await message.answer(
        "Что хотите добавить?",
        reply_markup=product_type_keyboard
    )

@router.message(
    StateFilter(AddDeposit.product_type)
)
async def choose_product_type(
        message: Message,
        state: FSMContext
):
    if message.text == "🏦 Вклад":

        await state.update_data(
            product_type="deposit"
        )

    elif message.text == "💳 Накопительный счет":

        await state.update_data(
            product_type="savings"
        )

    else:
        return await message.answer(
            "Выберите вариант из меню"
        )

    await state.set_state(
        AddDeposit.bank
    )

    msg = await message.answer(

        "➕ <b>Добавление продукта</b>\n\n"

        "Шаг 1/6\n\n"

        "🏦 Выберите банк:",

        reply_markup=banks_keyboard
    )

    await state.update_data(
        wizard_message_id=msg.message_id
    )

    try:
        await message.delete()
    except:
        pass

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

        "📄 <b>Введите название вклада</b>\n\n"

        "<blockquote>"
        "Например: Накопительный+"
        "</blockquote>",

        reply_markup=wizard_keyboard(
            "bank"
        )
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

            "📄 <b>Введите название вклада</b>\n\n"

            "<blockquote>"
            "Например: Накопительный+"
            "</blockquote>"
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
        await message.bot.edit_message_text(

            chat_id=message.chat.id,

            message_id=data[
                "wizard_message_id"
            ],

            parse_mode="HTML",

            text=(

                "➕ <b>Добавление вклада</b>\n\n"

                "Шаг 3/6\n\n"

                "💰 <b>Введите сумму вклада</b>\n\n"

                "<blockquote>"
                "Например: 500000"
                "</blockquote>"
            ),

            reply_markup=wizard_keyboard(
                "deposit_name"
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
        await message.delete()

    except Exception as e:
        print(e)


@router.message(
    StateFilter(AddDeposit.amount)
)
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
    await message.bot.edit_message_text(

        chat_id=message.chat.id,

        message_id=data[
            "wizard_message_id"
        ],

        text=(

            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 4/6\n\n"

            "📈 <b>Введите процентную ставку</b>\n\n"

            "<blockquote>"
            "Например: 15 или 14.5"
            "</blockquote>"
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

        await message.delete()

    except Exception as e:
        print(e)


@router.message(
    StateFilter(AddDeposit.rate)
)
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
    await message.bot.edit_message_text(

        chat_id=message.chat.id,

        message_id=data[
            "wizard_message_id"
        ],

        text=(

            "➕ <b>Добавление вклада</b>\n\n"

            "Шаг 5/6\n\n"

            "⏳ <b>Введите срок вклада в месяцах</b>\n\n"

            "<blockquote>"
            "Например: 12"
            "</blockquote>"
        ),

        reply_markup=wizard_keyboard(
            "rate"
        )
    )

    try:

        await message.delete()

    except Exception as e:
        print(e)

    await state.update_data(
        rate=rate
    )

    data = await state.get_data()

    if data["product_type"] == "savings":

        await message.bot.edit_message_text(

            chat_id=message.chat.id,

            message_id=data[
                "wizard_message_id"
            ],

            text=(

                "➕ <b>Добавление продукта</b>\n\n"

                "Шаг 5/5\n\n"

                "📅 Когда открыт счет?"
            ),

            reply_markup=open_date_keyboard
        )

        await state.set_state(
            AddDeposit.choose_open_date
        )

    else:

        await state.set_state(
            AddDeposit.months
        )


@router.message(
    StateFilter(AddDeposit.months)
)
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

        await message.delete()

    except Exception as e:
        print(e)

    await state.update_data(
        months=months
    )

    await state.set_state(
        AddDeposit.choose_open_date
    )


@router.callback_query(F.data == "date_today")
async def today_open_date(callback: CallbackQuery, state: FSMContext):

    await proceed_to_capitalization(
        callback,
        state,
        datetime.utcnow()
    )



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
        reply_markup=await build_calendar()
    )

    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback: CallbackQuery, callback_data: dict, state: FSMContext):

    selected, date = await SimpleCalendar().process_selection(
        callback,
        callback_data
    )

    if not selected:
        return

    if not validate_calendar_date(date):
        await callback.message.edit_text(
            "❌ Дата не может быть в будущем",
            reply_markup=await build_calendar()
        )
        await callback.answer()
        return

    await proceed_to_capitalization(
        callback,
        state,
        date
    )


async def proceed_to_capitalization(
    callback: CallbackQuery,
    state: FSMContext,
    created_at: datetime
):
    await state.update_data(created_at=created_at)

    await state.set_state(AddDeposit.capitalization)

    await callback.message.edit_text(
        "📈 Капитализация процентов?",
        reply_markup=capitalization_keyboard
    )

    await callback.answer()

@router.callback_query(
    StateFilter(AddDeposit.capitalization),
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
            product_type=data["product_type"],
            bank=data["bank"],
            deposit_name=data["deposit_name"],
            amount=data["amount"],
            rate=data["rate"],
            months=0 if data.get("product_type") == "savings"
            else data.get("months"),
            created_at=data["created_at"],
            capitalization=data["capitalization"]
        )

        session.add(deposit)

        await session.commit()

        await session.refresh(
            deposit
        )

        await log_action(
            user_id=callback.from_user.id,

            action="ADD_DEPOSIT",

            text=(
                f"{data['bank']} | "
                f"{data['amount']} ₽ | "
                f"{data['rate']}%"
            )
        )

    await callback.message.delete()

    product_name = (
        "Накопительный счет"
        if data["product_type"] == "savings"
        else "Вклад"
    )

    await callback.message.answer(
        f"✅ <b>{product_name} успешно добавлен</b>\n\n"
        "🎉 Все данные сохранены",
        reply_markup=main_keyboard
    )

    await send_deposit_card(
        callback.message,
        deposit
    )

    await callback.answer()

    await state.clear()