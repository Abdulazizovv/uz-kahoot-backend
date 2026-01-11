from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    full_name = State()
    phone_number = State()
