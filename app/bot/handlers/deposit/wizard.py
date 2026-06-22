from app.core.imports import *

router = Router()

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

            "💰 <b>Введите сумму вклада</b>\n\n"

            "<blockquote>"
            "Например: 500000"
            "</blockquote>",

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