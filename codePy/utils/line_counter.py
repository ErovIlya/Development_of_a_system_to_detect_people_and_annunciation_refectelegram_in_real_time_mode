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
    temp_position: int      # -1 - находится слева от линии, 0 - пересекает,1 - находится справа от линии
                            # (на текущем кадре)
    old_position: int       # -1 - находится слева от линии, 0 - пересекает,1 - находится справа от линии
                            # (на предыдущем кадре)

    def __init__(self, tracker_id, direction: int, is_intersect: bool = False):
        """
        :param tracker_id: ID объекта
        :param direction: текущее положение, относительно Line
        :param is_intersect: пересёк ли объект линию (по умолчанию False)
        """
        self.tracker_id = tracker_id
        self.direction = direction
        self.temp_position = direction
        self.is_intersect = is_intersect

    def __eq__(self, tracker_id: int) -> bool:
        """
        Переопределение равенства
        :param tracker_id: ID обнаружения, с которым происходит сравнение
        :return:
        """
        return self.tracker_id == tracker_id

    def intersect(self, position) -> [bool, int]:
        """
        Определение, пересёк ли данный объект Line
        :param position: текущая позиция относительно Line на кадре
        :return: 1) Пересёк ли объект Line 2) Если да, то в каком направлении\
        1 - слева направо, -1 - справа налево
        """
        print(f"{self.tracker_id}: {self.temp_position} -> {position}")
        if self.temp_position != position:
            result2 = 1 if self.temp_position <= 0 else -1
            self.old_position = self.temp_position
            self.temp_position = position
            print(f"{self.tracker_id} пересёк линию: {result2}")
            return True, result2
        self.old_position = self.temp_position
        return False, self.temp_position


# TODO: переписать алгоритм (работает неверно)
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

    def _f(self, point: Point) -> float:
        """
        Вспомогательная функция, которая нужна для определения, где лежит точка обнаружения
        """
        return self._a * point.x + self._b * point.y + self._c

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

    def __detected_object_intersection__(self, xyxy: np.ndarray, tracker_id: int) -> None:
        """
        Определение объекта (прямоугольника), который пересёк или нет Line
        :param xyxy: список координат объекта вида xyxy (левый верхний - нижний правый)
        :param tracker_id: id объекта
        """
        point_detected = self.__detected_point_object__(xyxy)
        detection = self.get_detected_object(tracker_id)
        if detection is not None:
            result_bool, result_position = detection.intersect(1 if self._f(point_detected) > 0 else -1)
            if result_bool:
                if self.start_point.x > self.end_point.x:
                    x1 = self.start_point.x
                    x2 = self.end_point.x
                else:
                    x2 = self.start_point.x
                    x1 = self.end_point.x
                if self.start_point.y > self.end_point.y:
                    y1 = self.start_point.y
                    y2 = self.end_point.y
                else:
                    y2 = self.start_point.y
                    y1 = self.end_point.y
                if not (x2 <= point_detected.x <= x1 and y2 <= point_detected.y <= y1):
                    return
                if result_position == 1:
                    self.in_count += 1
                else:
                    self.out_count += 1
        else:
            detection = DetectFromLine(tracker_id, 1 if self._f(point_detected) > 0 else -1)
        self.set_detected_object(detection)

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
            line: Line, frame: np.ndarray, color: Sequence[float] = (0, 255, 165), thickness: int = 5,
            text_point: Point = Point(100, 100)
    ):
        """
        Отображение Line на кадре
        :param line: объект класса Line, который нужно отобразить на кадре
        :param frame: текущий кадр
        :param color: цвет в формате BRG (по умолчанию оранжевый)
        :param thickness: толщина линий (по умолчанию 4)
        :param text_point: объект класса Point, где будет отображаться Текст
        :return: кадр в виде массива numpy с нарисованной Zone
        """
        new_frame = cv2.line(frame, line.start_point.to_list(), line.end_point.to_list(), color, thickness)
        text = f"In: {line.in_count}; Out: {line.out_count}"

        new_frame = cv2.putText(new_frame, text, text_point.to_list(), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (128, 0, 0), 3)

        return new_frame
