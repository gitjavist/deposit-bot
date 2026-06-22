from decimal import Decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta


def calculate_deposit_stats(deposit):
    """
    Единый расчёт всех параметров вклада / накопительного счёта
    """

    is_savings = deposit.product_type == "savings"

    # =========================
    # SAVINGS
    # =========================
    if is_savings:
        monthly_profit = (
            deposit.amount
            * deposit.rate
            / Decimal("100")
            / Decimal("12")
        )

        return {
            "type": "savings",
            "monthly_profit": monthly_profit,
            "is_closed": False,
            "end_date": None,
            "total": None,
            "profit": None,
            "days_left": None,
            "progress_percent": None,
        }

    # =========================
    # DEPOSIT
    # =========================

    end_date = deposit.created_at + relativedelta(months=deposit.months)

    total_days = (end_date - deposit.created_at).days
    passed_days = (datetime.utcnow() - deposit.created_at).days

    if passed_days < 0:
        passed_days = 0

    days_left = max(total_days - passed_days, 0)

    progress_percent = min(
        int((passed_days / total_days) * 100) if total_days > 0 else 0,
        100
    )

    is_closed = end_date <= datetime.utcnow()

    # прибыль
    if deposit.capitalization:
        total = deposit.amount * (
            (
                Decimal("1")
                + deposit.rate / Decimal("100") / Decimal("12")
            ) ** deposit.months
        )
        profit = total - deposit.amount
    else:
        profit = (
            deposit.amount
            * (deposit.rate / Decimal("100"))
            * Decimal(total_days)
            / Decimal("365")
        )
        total = deposit.amount + profit

    return {
        "type": "deposit",
        "end_date": end_date,
        "total": total,
        "profit": profit,
        "days_left": days_left,
        "progress_percent": progress_percent,
        "is_closed": is_closed,
    }