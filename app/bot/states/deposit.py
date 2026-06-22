from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class AddDeposit(StatesGroup):
    product_type = State()
    bank = State()
    deposit_name = State()
    amount = State()
    rate = State()
    months = State()
    choose_open_date = State()
    capitalization = State()
    edit_name = State()
    edit_date = State()

