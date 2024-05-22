from codePy.utils.line_counter import Point, WhichPointObjectBeTracked
import matplotlib.path as mlt
from functools import partial
from typing import Sequence
from operator import is_not
import supervision as sv
import numpy as np
import cv2


class Zone:
    """
    Класс Zone служит для отображения и детектирования людей в некой области, задаваемой 3-5 точками
    """
    __count_points__: int
    _object_detected_point: int
    point1: Point
    point2: Point
    point3: Point
    point4: Point or None
    point5: Point or None

    def __init__(self, points: list[Point], position_object: int = WhichPointObjectBeTracked.center()) -> None:
        """
        :param points: список Point, которыми определена Zone
        :param position_object: по какой точке происходит детектирование объектов/n
        (смотри класс WhichPointObjectBeTracked)
        """
        points = list(filter(partial(is_not, None), points))
        self.point1 = points[0]
        self.point2 = points[1]
        self.point3 = points[2]
        self.point4 = points[3] if len(points) > 3 else None
        self.point5 = points[4] if len(points) > 4 else None
        self._count_points = len(points)
        self._object_detected_point = position_object

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

    def __polygon_to_tuple__(self) -> tuple:
        """
        Перевод точек, которые определяют Zone, в кортеж
        """
        if self._count_points == 5:
            return (self.point1.to_tuple(), self.point2.to_tuple(), self.point3.to_tuple(),
                    self.point4.to_tuple(), self.point5.to_tuple())
        elif self._count_points == 4:
            return (self.point1.to_tuple(), self.point2.to_tuple(), self.point3.to_tuple(),
                    self.point4.to_tuple())
        else:
            return self.point1.to_tuple(), self.point2.to_tuple(), self.point3.to_tuple()

    def __detected_object_in_zone__(self, xyxy: np.ndarray) -> bool:
        """
        Определяет, содержится ли объект в Zone по "особой" точке
        :param xyxy: координаты прямоугольника объекта
        """
        point_detected = self.__detected_point_object__(xyxy)
        path = mlt.Path(self.__polygon_to_tuple__())
        return path.contains_point(point_detected.to_tuple())

    def trigger(self, detections: sv.Detections) -> np.ndarray:
        """
        Определение объектов (прямоугольников), которые находятся в Zone
        :param detections: список обнаружений
        :return: список булевых объектов, отображающие входит ли объект в Zone или нет/
        (для каждого обнаружения из detections)
        """

        detections_in_zone = np.array([self.__detected_object_in_zone__(detection[0]) for detection in detections])
        return detections_in_zone.astype(bool)


class ZoneBoxAnnotated:
    """
    Класс для отображения Zone на кадре
    """
    @staticmethod
    def annotate(
            zone: Zone, frame: np.ndarray, color: Sequence[float] = (0, 0, 255), thickness: int = 4
    ):
        """
        Отображение Zone на кадре
        :param zone: объект класса Zone, который нужно отобразить на кадре
        :param frame: текущий кадр
        :param color: цвет в формате BRG (по умолчанию красный)
        :param thickness: толщина линий (по умолчанию 4)
        :return: кадр в виде массива numpy с нарисованной Zone
        """
        new_frame = cv2.line(frame, zone.point1.to_tuple(), zone.point2.to_tuple(), color, thickness)       # 1-2
        new_frame = cv2.line(new_frame, zone.point2.to_tuple(), zone.point3.to_tuple(), color, thickness)   # 2-3
        if zone.point4 is None:
            return cv2.line(new_frame, zone.point3.to_tuple(), zone.point1.to_tuple(), color, thickness)    # 3-1
        new_frame = cv2.line(new_frame, zone.point3.to_tuple(), zone.point4.to_tuple(), color, thickness)   # 3-4
        if zone.point5 is None:
            return cv2.line(new_frame, zone.point4.to_tuple(), zone.point1.to_tuple(), color, thickness)    # 4-1
        new_frame = cv2.line(new_frame, zone.point4.to_tuple(), zone.point5.to_tuple(), color, thickness)   # 4-5
        return cv2.line(new_frame, zone.point5.to_tuple(), zone.point1.to_tuple(), color, thickness)        # 5-1


def create_null_zone() -> Zone:
    """
    Создание пустого объекта Zone (не стоит использовать)
    :return:
    """
    return Zone([Point(0, 0), Point(0, 0), Point(0, 0)])
