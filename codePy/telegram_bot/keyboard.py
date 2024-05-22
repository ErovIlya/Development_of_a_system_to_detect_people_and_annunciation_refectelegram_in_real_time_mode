from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from codePy.telegram_bot.state_for_bot import Form


# task1_button = KeyboardButton(text='/task1')
# task2_button = KeyboardButton(text='/task2')
video_task1_button = KeyboardButton(text='/task1')
video_task2_button = KeyboardButton(text='/task2')
system_button = KeyboardButton(text='/system')
hi_button = KeyboardButton(text='/hi')
info_button = KeyboardButton(text='/info')
photo_button = KeyboardButton(text='/photo')
status_button = KeyboardButton(text='/status')
stop_button = KeyboardButton(text='/stop')
clear_button = KeyboardButton(text='/clear')

download_button = KeyboardButton(text='/download')
line_button = KeyboardButton(text='/set_line')
zone_button = KeyboardButton(text='/set_zone')
point_button = KeyboardButton(text='/set_point')
cancel_button = KeyboardButton(text='/cancel')
next_button = KeyboardButton(text='/next')

keyboard_after_download_video = ReplyKeyboardMarkup(
    keyboard=[
        [hi_button, system_button, info_button, clear_button],
        [video_task1_button, video_task2_button],
        [line_button, zone_button, download_button, point_button]
    ],
    resize_keyboard=True
)
keyboard_after_set_line = ReplyKeyboardMarkup(
    keyboard=[
        [next_button, cancel_button],
        [hi_button, system_button, info_button, clear_button],
        [photo_button]
    ],
    resize_keyboard=True
)

keyboard_start = ReplyKeyboardMarkup(
    keyboard=[
        [hi_button, system_button, info_button, clear_button], [video_task1_button, video_task2_button],
        [line_button, zone_button, download_button]
    ],
    resize_keyboard=True
)
keyboard_task = ReplyKeyboardMarkup(
    keyboard=[
        [status_button, stop_button, clear_button], [hi_button, system_button, info_button]
    ],
    resize_keyboard=True
)
keyboard_video = ReplyKeyboardMarkup(
    keyboard=[
        [stop_button], [hi_button, system_button, info_button, clear_button]
    ]
)
keyboard_download = ReplyKeyboardMarkup(
    keyboard=[
        [cancel_button], [hi_button, system_button, info_button, clear_button]
    ]
)
keyboard_set_sp_point = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Центр прямоугольника")],
        [KeyboardButton(text="Центр нижнего ребра"), KeyboardButton(text="Центр верхнего ребра")],
        [KeyboardButton(text="Центр правого ребра"), KeyboardButton(text="Центр левого ребра")]
    ],
    resize_keyboard = True
)


def get_keyboard(_state) -> ReplyKeyboardMarkup:
    """
    Вернуть клавиатуру в зависимости от состояния пользователя
    :param _state: Полученное состояние, в котором находится пользователь (FSMContext.get_state())
    """
    if _state == Form.start:
        return keyboard_task
    elif _state == Form.search:
        return keyboard_video
    elif _state in [Form.line_state, Form.line_test]:
        return keyboard_after_set_line
    else:
        return keyboard_start
