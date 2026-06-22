from aiogram.fsm.state import (
    State,
    StatesGroup
)


class DeleteDeposit(StatesGroup):
    deposit_id = State()