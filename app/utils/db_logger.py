from app.database.database import (
    async_session
)

from app.database.models.log import (
    UserLog
)


async def log_action(
        user_id: int,
        action: str,
        text: str = None
):
    async with async_session() as session:

        log = UserLog(
            user_id=user_id,
            action=action,
            text=text
        )

        session.add(log)

        await session.commit()
