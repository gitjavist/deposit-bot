from aiogram.fsm.state import (
    State,
    StatesGroup
)


class EditDeposit(StatesGroup):
    amount = State()
    rate = State()
    months = State()
    edit_name = State()
    edit_date = State()