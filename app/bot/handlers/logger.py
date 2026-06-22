from app.core.imports import *

router = Router()

@router.message()
async def all_messages_logger(
        message: Message
):
    await log_action(
        user_id=message.from_user.id,

        action="MESSAGE",

        text=message.text
    )