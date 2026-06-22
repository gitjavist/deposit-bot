from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Boolean,
    Integer
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True
    )

    username: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    first_name: Mapped[str] = mapped_column(
        String(100)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    timezone: Mapped[str] = mapped_column(
        String(50),
        default="Europe/Moscow"
    )

    notification_hour: Mapped[int] = mapped_column(
        Integer,
        default=10
    )

    deposit_view_mode: Mapped[str] = mapped_column(
        String(20),
        default="list"
    )