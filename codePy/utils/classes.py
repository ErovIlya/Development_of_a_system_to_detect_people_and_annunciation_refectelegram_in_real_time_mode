from codePy.telegram_bot.clear_status import clear_status
from codePy.telegram_bot.create_bot import TOKEN_API
from aiogram.types import FSInputFile
from datetime import datetime
from threading import Event
import supervision as sv
from aiogram import Bot
from typing import Dict
import numpy as np


class User:
    """
    Класс User служит для удобного размещения информации об пользователе/чате
    """
    chat_id: int
    stop_event: Event
    status_event: Event

    def __init__(self, chat_id: int, stop_event: Event, status_event: Event):
        self.chat_id = chat_id
        self._bot = Bot(TOKEN_API)
        self._stop_event = stop_event
        self._status_event = status_event

    async def send_message(self, text: str) -> None:
        """
        Отправка пользователю сообщения
        """
        await self._bot.send_message(self.chat_id, text)

    async def send_photo(self, text: str, path: str) -> None:
        """
        Отправка пользователю фотографии
        """
        photo = FSInputFile(path)
        await self._bot.send_photo(self.chat_id, photo, caption=text)

    def check_stop_event(self) -> bool:
        """
        Проверка, что пользователь хочет остановить задачу
        """
        return self._stop_event.is_set()

    def clear_stop_event(self) -> None:
        """
        Очистка "Stop_Event"
        """
        self._stop_event.clear()

    def check_status_event(self) -> bool:
        """
        Проверка, что пользователь хочет вывести промежуточный итог задачи
        """
        return self._status_event.is_set()

    def clear_status_event(self) -> None:
        """
        Очистка "Status_Event"
        """
        self._status_event.clear()

    async def close_bot(self) -> None:
        """
        Отключение дополнительного бота для отправки сообщений
        """
        await self._bot.session.close()

    async def clear_status(self) -> None:
        """
        Очистка состояния пользователя
        """
        await clear_status(self.chat_id)


_s_list_task1 = {'download': 10, 'search': 11, 'stream': 12, 'end': 13}
_s_list_task2 = {'download': 20, 'search': 21, 'stream': 22, 'end': 23}
_s_list_task3 = {'download': 30, 'search': 31, 'stream': 32, 'end': 33}


class StateForTask1:
    """
    Состояния, которые может принять программа при выполнении задачи 1
    """
    @staticmethod
    def download() -> int:
        """
        Загрузка видео (будет позже)
        """
        return _s_list_task1['download']

    @staticmethod
    def search() -> int:
        """
        Поиск и формирование видео
        """
        return _s_list_task1['search']

    @staticmethod
    def stream() -> int:
        """
        Прямой вывод видео (с большой задержкой) и результата в телеграм
        """
        return _s_list_task1['stream']

    @staticmethod
    def end() -> int:
        """
        Выгрузка видео в телеграм (будет позже)
        """
        return _s_list_task1['end']


class StateForTask2:
    """
    Состояния, которые может принять программа при выполнении задачи 2
    """
    @staticmethod
    def download() -> int:
        """
        Загрузка видео (будет позже)
        """
        return _s_list_task2['download']

    @staticmethod
    def search() -> int:
        """
        Поиск и формирование видео
        """
        return _s_list_task2['search']

    @staticmethod
    def stream() -> int:
        """
        Прямой вывод видео (с большой задержкой) и результата в телеграм
        """
        return _s_list_task2['stream']

    @staticmethod
    def end() -> int:
        """
        Выгрузка видео в телеграм (будет позже)
        """
        return _s_list_task2['end']


class FPSBaseTimer:
    """
    Таймер для подсчёта времени нахождения объекта на видео файле\n
    Основан на FPS\n
    Видео файл ДОЛЖЕН обладать чётким и постоянным FPS\n
    (Не рекомендуется к использованию при запуске через поток)
    """
    def __init__(self, fps: int = 30) -> None:
        """
        Инициализация FPSBaseTimer
        """
        self.fps = fps
        self.frame_id = 0
        self.tracker_id2frame_id: Dict[int, int] = {}

    def tick(self, detections: sv.Detections) -> np.ndarray:
        """
        Обрабатывает текущий кадр, обновляя временные интервалы для каждого трекера
        :param detections: обнаружения на текущем кадре
        """
        self.frame_id += 1
        times = []

        for tracker_id in detections.tracker_id:
            self.tracker_id2frame_id.setdefault(tracker_id, self.frame_id)

            start_frame_id = self.tracker_id2frame_id[tracker_id]
            time_duration = (self.frame_id - start_frame_id) / self.fps
            times.append(time_duration)

        return np.array(times)


class ClockBasedTimer:
    """
    Таймер для подсчёта времени нахождения объекта на видео файле\n
    Основан на основе часов\n
    """
    def __init__(self) -> None:
        """
        Инициализация ClockBasedTimer
        """
        self.tracker_id2frame_id: Dict[int, datetime] = {}

    def tick(self, detections: sv.Detections) -> np.ndarray:
        """
        Обрабатывает текущий кадр, обновляя временные интервалы для каждого трекера
        :param detections: обнаружения на текущем кадре
        """
        current_time = datetime.now()
        times = []

        for tracker_id in detections.tracker_id:
            self.tracker_id2frame_id.setdefault(tracker_id, current_time)

            start_time = self.tracker_id2frame_id[tracker_id]
            time_duration = (current_time - start_time).total_seconds()
            times.append(time_duration)

        return np.array(times)
