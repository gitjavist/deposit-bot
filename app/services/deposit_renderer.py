from app.services.deposit_calculator import (
    calculate_deposit_stats
)


def render_short_card(deposit):

    stats = calculate_deposit_stats(
        deposit
    )

    if deposit.product_type == "savings":

        monthly_profit = (
            stats["monthly_profit"]
        )

        return (
            f"💳 <b>{deposit.bank}</b>\n\n"
            f"📂 <b>Накопительный счет</b>\n\n"
            f"📄 <b>{deposit.deposit_name}</b>\n\n"
            f"💰 <b>{deposit.amount:,.2f} ₽</b>\n\n"
            f"📈 <b>{deposit.rate}%</b>\n\n"
            f"💵 В месяц:\n"
            f"<b>{monthly_profit:,.2f} ₽</b>"
        )

    end_date = stats["end_date"]

    total = stats["total"]

    days_left = stats["days_left"]

    progress_percent = stats["progress_percent"]

    filled = int(progress_percent / 10)

    progress_bar = (
        "█" * filled +
        "░" * (10 - filled)
    )

    return (
        f"🏦 <b>{deposit.bank}</b>\n\n"
        f"📄 <b>{deposit.deposit_name}</b>\n\n"
        f"💰 <b>{deposit.amount:,.2f} ₽</b>\n"
        f"📈 <b>{deposit.rate}%</b>\n"
        f"⏳ <b>{deposit.months} мес.</b>\n\n"
        f"🏁 <b>{total:,.2f} ₽</b>\n"
        f"📅 <b>{end_date.strftime('%d.%m.%Y')}</b>\n"
        f"⏳ <b>{days_left} дн.</b>\n"
        f"{progress_bar} <b>{progress_percent}%</b>"
    )