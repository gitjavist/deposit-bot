from aiogram.fsm.state import (
    StatesGroup,
    State
)

class SettingsState(StatesGroup):
    notification_hour = State()