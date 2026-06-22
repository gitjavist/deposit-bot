from app.core.imports import *

router = Router()

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