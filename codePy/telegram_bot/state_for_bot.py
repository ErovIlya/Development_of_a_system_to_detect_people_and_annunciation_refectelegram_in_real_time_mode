from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    path_photo = State()    # Путь к последнему обработанному файлу
    path_video = State()    # Путь к последнему обработанному видео
    line = State()   # Координаты точек отрезка

    start = State()         # Происходит выполнение задачи детектирования
    search = State()        # Происходит обработка видео
    download = State()      # Выгрузка видео на ресурс
    point_state = State()   # Установка точек для отрезка
    point_test = State()    # Проверка, что отрезок установлен, как и хотел пользователь
