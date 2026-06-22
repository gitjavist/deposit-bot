from datetime import datetime

from sqlalchemy import select

from app.database.database import (
    async_session
)

from app.database.models.deposit import (
    Deposit
)

from aiogram import Bot


async def check_finished_deposits(
        bot: Bot
):
    async with async_session() as session:

        result = await session.execute(
            select(Deposit).where(
                Deposit.notified == False
            )
        )

        deposits = result.scalars().all()

        for deposit in deposits:

            end_date = (
                deposit.created_at
                + relativedelta(
                    months=deposit.months
                )
            )

            if end_date <= datetime.utcnow():

                profit = (
                    deposit.amount
                    * deposit.rate
                    / 100
                    * deposit.months
                    / 12
                )

                await bot.send_message(

                    deposit.user_id,

                    "🎉 <b>Вклад завершен</b>\n\n"

                    f"🏦 {deposit.bank}\n"

                    f"💰 "
                    f"{deposit.amount:,.2f} ₽\n"

                    f"📈 "
                    f"Доход: "
                    f"{profit:,.2f} ₽"
                )

                deposit.notified = True

        await session.commit()