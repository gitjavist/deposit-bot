from app.core.imports import *

from app.bot.keyboards.deposit_view_keyboard import (
    deposit_view_keyboard
)

router = Router()

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

    view_mode = (
        "📜 Списком"
        if user.deposit_view_mode == "list"
        else "📑 Постранично"
    )

    await message.answer(
        f"⚙ <b>Настройки</b>\n\n"

        f"🔔 Уведомления: "
        f"<b>{status}</b>\n\n"

        f"🌍 Часовой пояс:\n"
        f"<b>{user.timezone}</b>\n\n"

        f"⏰ Время уведомлений:\n"
        f"<b>{user.notification_hour}:00</b>\n\n"

        f"📑 Вид отображения вкладов:\n"
        f"<b>{view_mode}</b>\n\n",

        reply_markup=settings_keyboard(
            user.notifications_enabled
        )
    )

@router.callback_query(
    F.data == "open_view_settings"
)
async def deposit_view_settings(
        callback: CallbackQuery
):
    async with async_session() as session:
        query = select(User).where(
            User.telegram_id
            == callback.from_user.id
        )

        result = await session.execute(query)

        user = result.scalar()

    current_mode = (
        "📜 Списком"
        if user.deposit_view_mode == "list"
        else "📑 Постранично"
    )

    await callback.message.answer(

        "📑 <b>Выберите режим отображения вкладов</b>\n\n"

        f"Текущий режим:\n"
        f"<b>{current_mode}</b>\n\n"

        "📜 Списком — все вклады сразу\n"
        "📑 Постранично — по одному вкладу",

        reply_markup=deposit_view_keyboard
    )

@router.callback_query(
    F.data.in_([
        "view_list",
        "view_pagination"
    ])
)
async def change_view_mode(
        callback: CallbackQuery
):
    mode = (
        "list"
        if callback.data == "view_list"
        else "pagination"
    )

    async with async_session() as session:

        query = select(User).where(
            User.telegram_id
            == callback.from_user.id
        )

        result = await session.execute(query)

        user = result.scalar()

        user.deposit_view_mode = mode

        await session.commit()

    await callback.message.edit_text(

        "✅ Настройка сохранена\n\n"

        f"Текущий режим: "
        f"{'📜 Списком' if mode == 'list' else '📑 Постранично'}"
    )

    await callback.answer()


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
    F.data == "change_notification_hour"
)
async def change_notification_hour(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.set_state(
        SettingsState.notification_hour
    )

    await callback.message.answer(

        "⏰ <b>Введите час уведомлений</b>\n\n"

        "Введите число от 0 до 23",

        reply_markup=cancel_keyboard
    )

    await callback.answer()


@router.message(
    SettingsState.notification_hour
)
async def set_notification_hour(
        message: Message,
        state: FSMContext
):
    if message.text == "❌ Отмена":
        await state.clear()

        await message.answer(
            "❌ Изменение времени уведомлений отменено",
            reply_markup=main_keyboard
        )

        return

    try:

        hour = int(message.text)

    except ValueError:

        await message.answer(
            "❌ Введите число от 0 до 23"
        )

        return

    if hour < 0 or hour > 23:

        await message.answer(
            "❌ Час должен быть от 0 до 23"
        )

        return

    async with async_session() as session:

        query = select(User).where(
            User.telegram_id
            == message.from_user.id
        )

        result = await session.execute(query)

        user = result.scalar()

        user.notification_hour = hour

        await session.commit()

    try:

        await message.delete()

    except Exception:
        pass

    await message.answer(

        f"✅ Время уведомлений изменено\n\n"

        f"⏰ Новое время:\n"
        f"<b>{hour}:00</b>",

        reply_markup=main_keyboard
    )

    await state.clear()