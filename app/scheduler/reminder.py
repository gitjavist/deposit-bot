from datetime import datetime, timedelta

from sqlalchemy import select

from zoneinfo import ZoneInfo

from app.database.models.user import User

from app.database.database import async_session
from app.database.models.deposit import Deposit

from dateutil.relativedelta import relativedelta

from app.services.deposit_calculator import (
    calculate_deposit_stats
)


async def check_deposits(bot):

    async with async_session() as session:

        query = select(Deposit)

        result = await session.execute(query)

        deposits = result.scalars().all()

        for deposit in deposits:

            if deposit.product_type == "savings":
                continue

            stats = calculate_deposit_stats(
                deposit
            )

            end_date = stats["end_date"]
            days_left = stats["days_left"]

            user_query = select(User).where(
                User.telegram_id == deposit.user_id
            )

            user_result = await session.execute(
                user_query
            )

            user = user_result.scalar()

            if not user:
                continue

            if not user.notifications_enabled:
                continue

            timezone = (
                user.timezone
                if user.timezone
                else "UTC"
            )

            user_now = datetime.now(
                ZoneInfo(timezone)
            )

            if user_now.hour != user.notification_hour:
                continue

            # Уведомление за 7 дней

            if (
                    days_left <= 7
                    and days_left > 1
                    and not deposit.notified_7_days
            ):
                profit = stats["profit"]
                total = stats["total"]

                await bot.send_message(

                    deposit.user_id,

                    "⏰ <b>Вклад скоро завершится</b>\n\n"

                    f"🏦 <b>{deposit.bank}</b>\n\n"

                    f"📄 <b>{deposit.deposit_name}</b>\n\n"

                    f"💰 Сумма:\n"
                    f"<b>{deposit.amount:,.2f} ₽</b>\n\n"

                    f"💵 Прибыль:\n"
                    f"<b>{profit:,.2f} ₽</b>\n\n"

                    f"🏁 Итог:\n"
                    f"<b>{total:,.2f} ₽</b>\n\n"

                    f"📅 Закрытие:\n"
                    f"<b>{end_date.strftime('%d.%m.%Y')}</b>\n\n"

                    f"⏳ Осталось:\n"
                    f"<b>{days_left} дн.</b>"
                )

                deposit.notified_7_days = True

            # Уведомление за 1 день

            if (
                    days_left == 1
                    and not deposit.notified_1_day
            ):
                profit = stats["profit"]
                total = stats["total"]

                await bot.send_message(

                    deposit.user_id,

                    "🔥 <b>Вклад завершается завтра</b>\n\n"

                    f"🏦 <b>{deposit.bank}</b>\n\n"

                    f"📄 <b>{deposit.deposit_name}</b>\n\n"

                    f"💰 Вклад:\n"
                    f"<b>{deposit.amount:,.2f} ₽</b>\n\n"

                    f"💵 Доход:\n"
                    f"<b>{profit:,.2f} ₽</b>\n\n"

                    f"🏁 К получению:\n"
                    f"<b>{total:,.2f} ₽</b>\n\n"

                    f"📅 Дата закрытия:\n"
                    f"<b>{end_date.strftime('%d.%m.%Y')}</b>\n\n"

                    "⚠️ Не забудьте продлить вклад или вывести средства"
                )

                deposit.notified_1_day = True

            if (
                    end_date <= datetime.utcnow()
                    and not deposit.notified_finished
            ):
                profit = stats["profit"]

                if profit is None:
                    profit = 0

                profit = stats["profit"]
                total = stats["total"]

                await bot.send_message(

                    deposit.user_id,

                    "🎉 <b>Вклад завершён</b>\n\n"

                    f"🏦 <b>{deposit.bank}</b>\n\n"

                    f"📄 <b>{deposit.deposit_name}</b>\n\n"

                    f"💰 Вклад:\n"
                    f"<b>{deposit.amount:,.2f} ₽</b>\n\n"

                    f"💵 Полученная прибыль:\n"
                    f"<b>{profit:,.2f} ₽</b>\n\n"

                    f"🏁 Итоговая сумма:\n"
                    f"<b>{total:,.2f} ₽</b>\n\n"

                    f"📅 Дата завершения:\n"
                    f"<b>{end_date.strftime('%d.%m.%Y')}</b>"
                )

                deposit.notified_finished = True

        await session.commit()