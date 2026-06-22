from app.core.imports import *

from .cards import (
    send_deposit_card
)

router = Router()

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
        await message.delete()

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
        "✅ Сумма обновлена",
        reply_markup=main_keyboard
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
        await message.delete()

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
        "✅ Ставка обновлена",
        reply_markup=main_keyboard
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
        await message.delete()

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
        "✅ Срок обновлен",
        reply_markup=main_keyboard
    )

    await send_deposit_card(
        message,
        deposit
    )

    await state.clear()


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
        await message.delete()

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
        "✅ Название обновлено",
        reply_markup=main_keyboard
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
        await message.delete()

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
        "✅ Дата обновлена",
        reply_markup=main_keyboard
    )

    await state.clear()