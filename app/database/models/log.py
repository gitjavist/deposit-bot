from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Text
)

from datetime import datetime

from app.database.database import Base


class UserLog(Base):

    __tablename__ = "user_logs"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger
    )

    action: Mapped[str] = mapped_column(
        String(100)
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
