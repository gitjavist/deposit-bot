from datetime import datetime

from aiogram_calendar import (
    SimpleCalendar,
    SimpleCalendarCallback
)


async def build_calendar():
    return await SimpleCalendar().start_calendar()


def validate_calendar_date(date):
    return (
        date.date()
        <= datetime.utcnow().date()
    )