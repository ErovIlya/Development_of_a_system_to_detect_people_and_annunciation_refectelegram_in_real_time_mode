from codePy.telegram_bot.create_bot import TOKEN_API
from aiogram.types import FSInputFile
from threading import Event
from aiogram import Bot


class User:
    chat_id: int
    stop_event: Event
    status_event: Event

    def __init__(self, chat_id: int, stop_event: Event, status_event: Event):
        self.chat_id = chat_id
        self._bot = Bot(TOKEN_API)
        self._stop_event = stop_event
        self._status_event = status_event

    async def send_message(self, text: str):
        await self._bot.send_message(self.chat_id, text)

    async def send_photo(self, text: str, path: str):
        photo = FSInputFile(path)
        await self._bot.send_photo(self.chat_id, photo, caption=text)

    def check_stop_event(self) -> bool:
        return self._stop_event.is_set()

    def clear_stop_event(self) -> None:
        self._stop_event.clear()

    def check_status_event(self) -> bool:
        return self._status_event.is_set()

    def clear_status_event(self) -> None:
        self._status_event.clear()

    def close_bot(self) -> None:
        self._bot.session.close()


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_list(self):
        return [self.x, self.y]


class Line:
    start_point: Point
    end_point: Point
    _middle_point: Point

    is_convert = False
    _k: float
    _b: float

    """
        Ключ словаря - tracker_id (идентификатор человека)
        Значение словаря - список: певрый элемент - пересёк ли человек линию;
            второй элемент - в какой стороне от линии он находился ('right' или 'left')
    """
    _intersect_info: dict[int, list[bool, str]]
    in_coming = 0
    out_coming = 0

    def __init__(self, start_point: Point, end_point: Point):
        self.start_point = start_point
        self.end_point = end_point

    def convert(self) -> None:
        self.is_convert = True

        self._k = (self.start_point.y - self.end_point.y) / (self.start_point.x - self.end_point.x)
        self._b = self.end_point.y - self._k * self.end_point.x
        self._middle_point = Point(
            (self.start_point.x + self.end_point.x) / 2,
            (self.start_point.y + self.end_point.y) / 2
        )
        self._intersect_info = {}

    def check_convert(self) -> bool:
        return self.is_convert

    def _f(self, x, y) -> float:
        print(f"{y} - {self._k} * {x} - {self._b} = {y - self._k * x - self._b}")
        return y - self._k * x - self._b

    def _intersect(self, detection: list, tracker_id: int):
        f1 = self._f(detection[0], detection[1])
        f2 = self._f(detection[2], detection[3])
        intersect_bool = (f1 * f2 < 0 and detection[0] >= self.start_point.x and detection[2] <= self.end_point.x)

        if tracker_id not in self._intersect_info:
            temp_list = [intersect_bool]
            if self._middle_point.x <= detection[0]:
                temp_list.append('right')
            else:
                temp_list.append('left')
            self._intersect_info[tracker_id] = temp_list
            return

        temp_list = self._intersect_info[tracker_id]
        if intersect_bool and not temp_list[0]:
            temp_list[0] = True
            self._intersect_info[tracker_id] = temp_list
            return

        if f1 * f2 >= 0 and temp_list[0]:
            if temp_list[1] == 'right':
                self.out_coming += 1
            else:
                self.in_coming += 1
            self._intersect_info.pop(tracker_id)
            return

    def trigger(self, detections):
        for detection in detections:
            self._intersect(detection[0], detection[4])
        