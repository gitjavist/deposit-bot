from dotenv import load_dotenv
from pathlib import Path

import os

BASE_DIR = Path(
    __file__
).resolve().parent.parent.parent

load_dotenv(
    BASE_DIR / ".env"
)


class Config:

    BOT_TOKEN = os.getenv(
        "BOT_TOKEN"
    )

    ADMIN_ID = int(
        os.getenv("ADMIN_ID")
    )

    PROXY_URL = os.getenv(
            "PROXY_URL"
    )


ADMINS = [
    Config.ADMIN_ID
]