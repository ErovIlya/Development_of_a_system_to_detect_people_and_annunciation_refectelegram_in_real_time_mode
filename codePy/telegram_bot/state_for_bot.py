from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    path = State()
    start = State()
