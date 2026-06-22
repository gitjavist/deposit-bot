from app.config.config import ADMINS


def is_admin(user_id: int):

    return user_id in ADMINS