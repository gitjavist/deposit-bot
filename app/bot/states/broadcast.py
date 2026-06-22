from aiogram.fsm.state import (
    State,
    StatesGroup
)


class BroadcastState(StatesGroup):
    message = State()