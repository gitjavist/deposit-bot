from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    Numeric,
    Boolean
)

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.database import Base

from datetime import datetime
from sqlalchemy import DateTime


class Deposit(Base):
    __tablename__ = "deposits"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger
    )

    bank: Mapped[str] = mapped_column(
        String(100)
    )

    deposit_name: Mapped[str] = mapped_column(
        String(100)
    )

    product_type: Mapped[str] = mapped_column(
        String(20),
        default="deposit"
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2)
    )

    rate: Mapped[float] = mapped_column(
        Numeric(5, 2)
    )

    months: Mapped[int] = mapped_column(
        Integer
    )

    capitalization: Mapped[bool] = mapped_column(
        Boolean
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    notified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    notified_7_days: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    notified_1_day: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    notified_finished: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_closed: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )