from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    """
    Состояния, в которые может перейти пользователь
    """
    start = State()         # Происходит выполнение задачи детектирования
    search = State()        # Происходит обработка видео
    download = State()      # Загрузка видео на сервер из облака
    line_state = State()    # Установка точек для отрезка
    line_test = State()     # Проверка, что отрезок установлен, как и хотел пользователь
    zone_state = State()    # Установка точек для зоны
    zone_test = State()     # Проверка, что зона установлена, как и хотел пользователь
    point_state = State()   # Установка "особой" точки
