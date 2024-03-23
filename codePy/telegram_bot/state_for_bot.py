from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    path = State()
    start = State()
