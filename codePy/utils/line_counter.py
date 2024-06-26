from codePy.utils.classes_for_line_and_zone import Point, WhichPointObjectBeTracked
from typing import Sequence
import numpy as np
import cv2


class DetectFromLine:
    """
    Обнаруженные объекты, которые в дальнейшем пересекутся с Line
    """
    tracker_id: int
    is_intersect: bool
    temp_position: Point
    old_position: Point

    def __init__(self, tracker_id, direction: Point, is_intersect: bool = False):
        """
        :param tracker_id: ID объекта
        :param direction: текущее положение, относительно Line
        :param is_intersect: пересёк ли объект линию (по умолчанию False)
        """
        self.tracker_id = tracker_id
        self.direction = direction
        self.old_position = direction
        self.temp_position = direction
        self.is_intersect = is_intersect

    def __eq__(self, tracker_id: int) -> bool:
        """
        Переопределение равенства
        :param tracker_id: ID обнаружения, с которым происходит сравнение
        :return:
        """
        return self.tracker_id == tracker_id

    def change(self, position: Point) -> None:
        self.old_position = self.temp_position
        self.temp_position = position


class Line:
    """
    Класс Line - отрезок, через который необходимо отслеживать переходящих людей
    """
    start_point: Point
    end_point: Point
    _middle_point: Point
    _object_detected_point: int

    is_convert = False
    _a: float
    _b: float
    _c: float

    _intersect_info: list[DetectFromLine]
    in_count = 0
    out_count = 0

    def __init__(
            self, start_point: Point, end_point: Point, position_object: int = WhichPointObjectBeTracked.center()
    ) -> None:
        """
        :param start_point: первая Point для Line
        :param end_point: вторая Point для Line
        :param position_object: по какой точке происходит детектирование объектов\
        (смотри класс WhichPointObjectBeTracked)
        """
        self.start_point = start_point
        self.end_point = end_point
        self._object_detected_point = position_object

        self._a = self.start_point.y - self.end_point.y
        self._b = self.end_point.x - self.start_point.x
        self._c = -1 * (self._a * self.start_point.x + self._b * self.start_point.y)
        self._middle_point = Point(
            (self.start_point.x + self.end_point.x) / 2,
            (self.start_point.y + self.end_point.y) / 2
        )
        self._intersect_info = []

    def get_detected_object(self, tracker_id: int) -> DetectFromLine or None:
        """
        Возвращает объект обнаружения, о котором есть информация для Line, если он есть. Если нет, то None
        :param tracker_id: ID обнаружения
        """
        for detection in self._intersect_info:
            if detection == tracker_id:
                return detection
        return None

    def set_detected_object(self, detection: DetectFromLine) -> None:
        """
        Добавление обнаружения в информацию для Line
        :param detection: объект класса DetectFromLine
        """
        if self.get_detected_object(detection.tracker_id) is not None:
            self._intersect_info.remove(detection)
        self._intersect_info.append(detection)

    def __detected_point_object__(self, xyxy: np.ndarray) -> Point:
        """
        Определение "особой" точки класса Point, по которой происходит детектирование\
        (смотри класс WhichPointObjectBeTracked)
        :param xyxy: прямоугольник объекта в виде numpy массива
        """
        if self._object_detected_point == WhichPointObjectBeTracked.center():
            x = (xyxy[0] + xyxy[2]) / 2
            y = (xyxy[1] + xyxy[3]) / 2
            return Point(x, y)
        elif self._object_detected_point == WhichPointObjectBeTracked.up_center():
            x = (xyxy[0] + xyxy[2]) / 2
            y = xyxy[1]
            return Point(x, y)
        elif self._object_detected_point == WhichPointObjectBeTracked.bottom_center():
            x = (xyxy[0] + xyxy[2]) / 2
            y = xyxy[3]
            return Point(x, y)
        elif self._object_detected_point == WhichPointObjectBeTracked.left_center():
            x = xyxy[0]
            y = (xyxy[1] + xyxy[3]) / 2
            return Point(x, y)
        elif self._object_detected_point == WhichPointObjectBeTracked.right_center():
            x = xyxy[2]
            y = (xyxy[1] + xyxy[3]) / 2
            return Point(x, y)

    @staticmethod
    def on_segment(a: Point, b: Point, c: Point) -> bool:
        """
        Функция проверяет, лежит ли точка b на отрезке прямой ac
        """
        if ((b.x <= max(a.x, c.x)) and (b.x >= min(a.x, c.x)) and
                (b.y <= max(a.y, c.y)) and (b.y >= min(a.y, c.y))):
            return True
        return False

    @staticmethod
    def orientation(a: Point, b: Point, c: Point) -> int:
        """
        Функция находит ориентацию упорядоченного триплета (a, b, c)
        :return: 0 - Точки, расположенные на одной прямой, 1 - точки, расположенные по часовой стрелке, \
        2 - Точки, расположенные против часовой стрелки
        """
        val = (float(b.y - a.y) * (c.x - b.x)) - (float(b.x - a.x) * (c.y - b.y))
        if val > 0:
            # Ориентация по часовой
            return 1
        elif val < 0:
            # Ориентация против часовой стрелки
            return 2
        else:
            # Коллинеарная ориентация
            return 0

    def do_intersect(self, old_point: Point, temp_point: Point) -> bool:
        """
        Находит 4 ориентации для общего и частного случаев
        """
        o1 = self.orientation(old_point, temp_point, self.start_point)
        o2 = self.orientation(old_point, temp_point, self.end_point)
        o3 = self.orientation(self.start_point, self.end_point, old_point)
        o4 = self.orientation(self.start_point, self.end_point, temp_point)

        # Общий случай
        if (o1 != o2) and (o3 != o4):
            return True

        # Особые случаи

        # p1, q1 и p2 коллинеарны и p2 лежит на p1q1
        if (o1 == 0) and self.on_segment(old_point, self.start_point, temp_point):
            return True

        # p1, q1 и q2 коллинеарны и q2 лежит на p1q1
        if (o2 == 0) and self.on_segment(old_point, self.end_point, temp_point):
            return True

        # p2, q2 и p1 коллинеарны и p1 лежит на p2q2
        if (o3 == 0) and self.on_segment(self.start_point, old_point, self.end_point):
            return True

        # p2, q2 и q1 коллинеарны и q1 лежит на p2q2
        if (o4 == 0) and self.on_segment(self.start_point, temp_point, self.end_point):
            return True

        # Если ничего не подходит
        return False

    def choosing_side(self, position: Point) -> int:
        """
        Вспомогательная функция, которая нужна для определения, где лежит точка обнаружения
        """
        return 1 if self._a * position.x + self._b * position.y + self._c >= 0 else -1

    def __detected_object_intersection__(self, xyxy: np.ndarray, tracker_id: int) -> None:
        special_point = self.__detected_point_object__(xyxy)
        detect = self.get_detected_object(tracker_id)
        if detect is None:
            self.set_detected_object(DetectFromLine(tracker_id, special_point))
            return
        if detect.is_intersect:
            return
        old_position = detect.old_position
        result = self.do_intersect(old_position, special_point)
        if result:
            detect.is_intersect = True
            self.set_detected_object(detect)
            if self.choosing_side(special_point) == 1:
                self.out_count += 1
            else:
                self.in_count += 1

    def trigger(self, detections) -> None:
        """
        Определение и запись в список объектов (прямоугольников), которые пересекли или пересекают Line
        :param detections: список обнаружений
        """
        if len(detections) == 0:
            return
        for detection in detections:
            self.__detected_object_intersection__(detection[0], detection[4])


class LineBoxAnnotated:
    """
    Класс для отображения Line на кадре
    """
    @staticmethod
    def annotate(
            line: Line, frame: np.ndarray, color: Sequence[float] = (255, 165, 0), thickness: int = 5,
            text_point: Point = Point(100, 100), rectangle_point: Point = Point(70, 70)
    ):
        """
        Отображение Line на кадре
        :param line: объект класса Line, который нужно отобразить на кадре
        :param frame: текущий кадр
        :param color: цвет в формате BRG (по умолчанию оранжевый)
        :param thickness: толщина линий (по умолчанию 4)
        :param text_point: объект класса Point, где будет отображаться Текст
        :param rectangle_point: верхняя вершина прямоугольника под текстом
        :return: кадр в виде массива numpy с нарисованной Zone
        """
        rectangle_point2: Point = Point(
            270 + (count_digits_in_number(line.in_count) + count_digits_in_number(line.out_count)) * 27, 110
        )

        new_frame = cv2.line(frame, line.start_point.to_list(), line.end_point.to_list(), color, thickness)
        text = f"In: {line.in_count}; Out: {line.out_count}"
        new_frame = cv2.rectangle(new_frame, rectangle_point.to_list(), rectangle_point2.to_list(),
                                  (255, 255, 255), -1)
        new_frame = cv2.putText(new_frame, text, text_point.to_list(), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 0), 3)

        return new_frame


def count_digits_in_number(number: int) -> int:
    """
    Считает количество цифр в числе
    """
    count = 0
    if number < 10:
        return 1
    while number > 0:
        count += 1
        number = number // 10
    return count
