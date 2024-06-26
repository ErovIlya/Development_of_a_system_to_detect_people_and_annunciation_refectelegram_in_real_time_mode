import numpy as np

from codePy.utils.create_path_for_files import create_path_for_first_frame
from codePy.utils.line_counter import Line, LineBoxAnnotated
from codePy.utils.zone_counted import Zone, ZoneBoxAnnotated
from codePy.utils.classes_for_line_and_zone import Point
from PIL import Image, ImageDraw, ImageFont
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
    line = Line(Point(start_point[0], start_point[1]), Point(end_point[0], end_point[1]))

    path = create_path_for_first_frame()

    if success:
        path = draw_axes(
            LineBoxAnnotated.annotate(line, frame),
            int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )
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
    point1 = Point(points[0][0], points[0][1])
    point2 = Point(points[1][0], points[1][1])
    point3 = Point(points[2][0], points[2][1])
    point4 = Point(points[3][0], points[3][1]) if len(points) > 3 else None
    point5 = Point(points[4][0], points[4][1]) if len(points) > 4 else None
    zone = Zone([point1, point2, point3, point4, point5])
    video = cv2.VideoCapture(path_video)
    success, frame = video.read()

    if success:
        path = draw_axes(
            ZoneBoxAnnotated.annotate(zone, frame),
            int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )
    else:
        path = '../input/image/default.png'
    return path


def draw_axes(frame: np.ndarray, w: int, h: int) -> str:
    border_size = 100

    image = Image.fromarray(frame)
    white_image = Image.new("RGB", (w + 2 * border_size, h + 2 * border_size), (255, 255, 255))
    white_image.paste(image, (border_size, border_size))
    draw = ImageDraw.Draw(white_image)

    # Ось абсцисс
    draw.line(
        (border_size // 2, border_size - 10, w + 1.7 * border_size, border_size - 10),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (w + border_size, border_size + 10, w + 1.7 * border_size, border_size - 10),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (w + border_size, border_size - 30, w + 1.7 * border_size, border_size - 10),
        fill=(199, 21, 133), width=10
    )

    # Ось ординат
    draw.line(
        (border_size - 10, border_size // 2, border_size - 10, h + 1.7 * border_size),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (border_size - 30, h + border_size, border_size - 10, h + 1.7 * border_size),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (border_size + 10, h + border_size, border_size - 10, h + 1.7 * border_size),
        fill=(199, 21, 133), width=10
    )

    # Засечки на оси абсцисс
    draw.line(
        (border_size + w / 4, border_size, border_size + w / 4, border_size - 20),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (border_size + w / 2, border_size + 7, border_size + w / 2, border_size - 27),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (border_size + 3 * w / 4, border_size, border_size + 3 * w / 4, border_size - 20),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (border_size + w, border_size + 7, border_size + w, border_size - 27),
        fill=(199, 21, 133), width=10
    )

    # Засечки на оси ординат
    draw.line(
        (border_size, border_size + h / 4, border_size - 20, border_size + h / 4),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (border_size + 7, border_size + h / 2, border_size - 27, border_size + h / 2),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (border_size, border_size + 3 * h / 4, border_size - 20, border_size + 3 * h / 4),
        fill=(199, 21, 133), width=10
    )
    draw.line(
        (border_size + 7, border_size + h, border_size - 27, border_size + h),
        fill=(199, 21, 133), width=10
    )

    # Подписи
    font_size = 60
    font = ImageFont.truetype("arial.ttf", font_size)
    color_text = (0, 0, 0)
    draw.text((border_size // 3, 0), "0", font=font, fill=color_text)
    draw.text((w / 2 + border_size // 2, 0), str(int(w / 2)), font=font, fill=color_text)
    draw.text((w + border_size // 2, 0), str(w), font=font, fill=color_text)

    height_text = sum(font.getmetrics())
    text_image = Image.new("RGB", (h // 500 * height_text, height_text), (255, 255, 255))
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0, 0), str(h), fill=color_text, font=font)
    rotated_text_image = text_image.rotate(90, expand=1)
    white_image.paste(rotated_text_image, (0, h + border_size // 3))
    text_image = Image.new("RGB", (h // 500 * height_text, height_text), (255, 255, 255))
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0, 0), str(h // 2), fill=color_text, font=font)
    rotated_text_image = text_image.rotate(90, expand=1)
    white_image.paste(rotated_text_image, (0, h // 2 + border_size // 3))

    path = create_path_for_first_frame()
    white_image.save(path)
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
