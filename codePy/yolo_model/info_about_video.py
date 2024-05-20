from codePy.utils.create_path_for_files import create_path_for_first_frame
from functools import partial
from operator import is_not
import cv2


def get_first_frame_for_line(path_video: str, start_point: [int, int], end_point: [int, int]) -> str:
    """
    Получить первый кадр видео с установленным пользователем отрезком
    :param path_video: относительный путь к видео файлу
    :param start_point: точка 1 вида xyxy (координаты типа int)
    :param end_point: точка 2 вида xyxy (координаты типа int)
    :return: относительный путь к файлу
    """
    video = cv2.VideoCapture(path_video)
    success, frame = video.read()

    path = create_path_for_first_frame()

    if success:
        cv2.line(frame, start_point, end_point, (255, 102, 102), 5)
        cv2.imwrite(path, frame)
    else:
        path = '../input/image/default.png'
    return path


def get_first_frame_for_zone(path_video: str, points: list[list[int]]) -> str:
    """
    Получить первый кадр видео с установленным пользователем отрезком
    :param path_video: относительный путь к видео файлу
    :param points: координаты точек вида xyxy от 3 до 5 штук (координаты типа int)
    :return: относительный путь к файлу
    """
    points = list(filter(partial(is_not, None), points))
    point1 = points[0]
    point2 = points[1]
    point3 = points[2]
    point4 = points[3] if len(points) > 3 else None
    point5 = points[4] if len(points) > 4 else None
    video = cv2.VideoCapture(path_video)
    success, frame = video.read()

    path = create_path_for_first_frame()

    if success:
        cv2.line(frame, point1, point2, (255, 102, 102), 5)     # 1 - 2
        cv2.line(frame, point2, point3, (255, 102, 102), 5)     # 2 - 3
        if point4 is None:
            cv2.line(frame, point3, point1, (255, 102, 102), 5)     # 3 - 1
        else:
            cv2.line(frame, point3, point4, (255, 102, 102), 5)     # 3 - 4
            if point5 is None:
                cv2.line(frame, point4, point1, (255, 102, 102), 5)  # 4 - 1
            else:
                cv2.line(frame, point4, point5, (255, 102, 102), 5)  # 4 - 5
                cv2.line(frame, point5, point1, (255, 102, 102), 5)  # 5 - 1
        cv2.imwrite(path, frame)
    else:
        path = '../input/image/default.png'
    return path


def get_size_frame(path_video: str) -> [int, int]:
    """
    Получить размеры видео файла
    :param path_video: относительный путь к видео файлу
    :return: кортеж из двух элементов: первый - ширина, второй - высота
    """
    video = cv2.VideoCapture(path_video)
    success, frame = video.read()

    if success:
        w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return [w, h]
    else:
        return [0, 0]
