from app.core.imports import *

from aiogram.types import (
    InlineKeyboardMarkup
)

from .cards import (
    render_short_card,
    deposit_card_keyboard,
    send_deposit_card
)

from app.bot.keyboards.products_keyboard import (
    products_keyboard
)

from app.bot.keyboards.pagination_keyboard import (
    pagination_keyboard
)

router = Router()

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

    await message.answer(
        "💼 <b>Мои продукты</b>\n\n"
        "Выберите раздел:",
        reply_markup=products_keyboard
    )


@router.callback_query(
    F.data == "products_deposits"
)
async def deposits_menu(
        callback: CallbackQuery
):
    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == callback.from_user.id,
            Deposit.product_type == "deposit"
        )

        result = await session.execute(query)

        deposits = result.scalars().all()

    active_deposits = []

    for deposit in deposits:

        end_date = (
            deposit.created_at
            + relativedelta(months=deposit.months)
        )

        if end_date > datetime.utcnow():
            active_deposits.append(deposit)

    if not active_deposits:
        await callback.message.edit_text(
            "❌ Активных вкладов нет"
        )
        await callback.answer()
        return

    page = 0
    deposit = active_deposits[page]

    text = render_short_card(deposit)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *deposit_card_keyboard(
                deposit.id,
                deposit.product_type,
                deposit.is_closed
            ).inline_keyboard,

            *pagination_keyboard(
                page,
                len(active_deposits),
                "active_page"
            ).inline_keyboard
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )

    await callback.answer()


@router.callback_query(
    F.data == "products_savings"
)
async def savings_accounts(
        callback: CallbackQuery
):
    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == callback.from_user.id,
            Deposit.product_type == "savings",
            Deposit.is_closed == False
        )

        result = await session.execute(query)

        accounts = result.scalars().all()

    if not accounts:
        await callback.message.edit_text(
            "❌ У вас нет накопительных счетов"
        )

        await callback.answer()
        return

    page = 0
    deposit = accounts[page]

    text = render_short_card(deposit)

    keyboard = InlineKeyboardMarkup(

        inline_keyboard=[

            *deposit_card_keyboard(
                deposit.id,
                deposit.product_type,
                deposit.is_closed
            ).inline_keyboard,

            *pagination_keyboard(
                page,
                len(accounts),
                "savings_page"
            ).inline_keyboard
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )

    await callback.answer()


@router.callback_query(
    F.data == "deposits_active"
)
async def active_deposits(
        callback: CallbackQuery
):
    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == callback.from_user.id,
            Deposit.product_type == "deposit"
        )

        result = await session.execute(query)

        deposits = result.scalars().all()

        user_query = select(User).where(
            User.telegram_id
            == callback.from_user.id
        )

        user_result = await session.execute(
            user_query
        )

        user = user_result.scalar()

    active_deposits = []

    for deposit in deposits:

        end_date = (
            deposit.created_at
            + relativedelta(
                months=deposit.months
            )
        )

        if end_date > datetime.utcnow():
            active_deposits.append(
                deposit
            )

    if not active_deposits:
        await callback.answer()

        await callback.message.answer(
            "❌ Активных вкладов нет"
        )

        return

    if user.deposit_view_mode == "list":

        for deposit in active_deposits:
            await send_deposit_card(
                callback.message,
                deposit
            )

    else:

        deposit = active_deposits[0]

        text = render_short_card(deposit)

        keyboard = InlineKeyboardMarkup(

            inline_keyboard=[

                *deposit_card_keyboard(
                    deposit.id,
                    deposit.product_type,
                    deposit.is_closed
                ).inline_keyboard,

                *pagination_keyboard(
                    0,
                    len(active_deposits),
                    "active_page"
                ).inline_keyboard
            ]
        )

        await callback.message.answer(

            text,

            reply_markup=keyboard
        )

    await callback.answer()


@router.callback_query(
    F.data == "products_closed"
)
async def closed_deposits(
        callback: CallbackQuery
):
    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == callback.from_user.id
        )

        result = await session.execute(query)

        deposits = result.scalars().all()

    closed_deposits = []

    for deposit in deposits:

        if (
                deposit.product_type == "savings"
                and deposit.is_closed
        ):
            closed_deposits.append(
                deposit
            )
            continue

        if deposit.product_type == "deposit":

            end_date = (
                    deposit.created_at
                    + relativedelta(
                months=deposit.months
            )
            )

            if end_date <= datetime.utcnow():
                closed_deposits.append(
                    deposit
                )

    if not closed_deposits:
        await callback.answer()

        await callback.message.answer(
            "❌ Завершенных вкладов нет"
        )

        return

    page = 0

    deposit = closed_deposits[page]

    text = render_short_card(
        deposit
    )

    keyboard = InlineKeyboardMarkup(

        inline_keyboard=[

            *deposit_card_keyboard(
                deposit.id,
                deposit.product_type,
                deposit.is_closed
            ).inline_keyboard,

            *pagination_keyboard(
                page,
                len(closed_deposits),
                "closed_page"
            ).inline_keyboard
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("active_page_")
)
async def active_page_handler(
        callback: CallbackQuery
):
    page = int(
        callback.data.split("_")[-1]
    )

    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == callback.from_user.id,
            Deposit.product_type == "deposit"
        )

        result = await session.execute(query)

        deposits = result.scalars().all()

        user_query = select(User).where(
            User.telegram_id
            == callback.from_user.id
        )

        user_result = await session.execute(
            user_query
        )

        user = user_result.scalar()

    active_deposits = []

    for deposit in deposits:

        end_date = (
            deposit.created_at
            + relativedelta(
                months=deposit.months
            )
        )

        if end_date > datetime.utcnow():

            active_deposits.append(
                deposit
            )

    if not active_deposits:

        await callback.answer(
            "Нет активных вкладов"
        )

        return

    deposit = active_deposits[page]

    text = render_short_card(deposit)

    keyboard = InlineKeyboardMarkup(

        inline_keyboard=[

            *deposit_card_keyboard(
                deposit.id,
                deposit.product_type,
                deposit.is_closed
            ).inline_keyboard,

            *pagination_keyboard(
                page,
                len(active_deposits),
                "active_page"
            ).inline_keyboard
        ]
    )

    await callback.message.edit_text(

        text,

        reply_markup=keyboard
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("savings_page_")
)
async def savings_page_handler(
        callback: CallbackQuery
):
    page = int(
        callback.data.split("_")[-1]
    )

    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == callback.from_user.id,
            Deposit.product_type == "savings",
            Deposit.is_closed == False
        )

        result = await session.execute(query)

        accounts = result.scalars().all()

    if not accounts:
        await callback.answer(
            "Нет накопительных счетов"
        )
        return

    deposit = accounts[page]

    text = render_short_card(
        deposit
    )

    keyboard = InlineKeyboardMarkup(

        inline_keyboard=[

            *deposit_card_keyboard(
                deposit.id,
                deposit.product_type,
                deposit.is_closed
            ).inline_keyboard,

            *pagination_keyboard(
                page,
                len(accounts),
                "savings_page"
            ).inline_keyboard
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("closed_page_")
)
async def closed_page_handler(
        callback: CallbackQuery
):
    page = int(
        callback.data.split("_")[-1]
    )

    async with async_session() as session:

        query = select(Deposit).where(
            Deposit.user_id == callback.from_user.id
        )

        result = await session.execute(query)

        deposits = result.scalars().all()

    closed_deposits = []

    for deposit in deposits:

        if (
                deposit.product_type == "savings"
                and deposit.is_closed
        ):
            closed_deposits.append(
                deposit
            )
            continue

        if deposit.product_type == "deposit":

            end_date = (
                    deposit.created_at
                    + relativedelta(
                months=deposit.months
            )
            )

            if end_date <= datetime.utcnow():
                closed_deposits.append(
                    deposit
                )

    if not closed_deposits:

        await callback.answer(
            "Нет завершённых продуктов"
        )

        return

    deposit = closed_deposits[page]

    text = render_short_card(
        deposit
    )

    keyboard = InlineKeyboardMarkup(

        inline_keyboard=[

            *deposit_card_keyboard(
                deposit.id,
                deposit.product_type,
                deposit.is_closed
            ).inline_keyboard,

            *pagination_keyboard(
                page,
                len(closed_deposits),
                "closed_page"
            ).inline_keyboard
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )

    await callback.answer()