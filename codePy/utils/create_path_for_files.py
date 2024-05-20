import re

from codePy.utils.loggind_file import log_info
from datetime import datetime
import os


def get_abs_path(remote_path) -> str:
    """
    Возвращает абсолютный путь к файлу в данном проекте
    :param remote_path: относительный путь к данному файлу (должен начинаться с ../)
    """
    return os.path.abspath(remote_path)


def create_path_for_download_photo() -> str:
    """
    Создаёт шаблон пути для фотографии, которую необходимо скачать
    :return: относительный путь к фотографии
    """
    now_date = datetime.now().strftime('%d-%m-%Y')
    now_time = datetime.now().strftime('%H-%M-%S')

    if not os.path.exists('../download'):
        os.mkdir('../download')
        log_info("Создана папка '/download'")

    if not os.path.exists('../download/photo'):
        os.mkdir('../download/photo')
        log_info("Создана папка '/download/photo'")

    if not os.path.exists(f'../download/photo/{now_date}'):
        os.mkdir(f'../download/photo/{now_date}')
        log_info(f"Создана папка '/download/photo/{now_date}'")

    return f'../download/photo/{now_date}/{now_time}.png'


def create_path_for_image(path_img: str) -> str:
    """
    Создаёт шаблон пути для фотографии, которую необходимо обработать
    :return: относительный путь к фотографии
    """
    t_path = path_img.split('/')
    t_time = t_path[-1]
    t_date = t_path[-2]
    if not os.path.exists('../output'):
        os.mkdir('../output')
        log_info("Создана папка '/output'")
    if not os.path.exists('../output/from_image'):
        os.mkdir('../output/from_image')
        log_info("Создана папка '/output/from_image'")
    if not os.path.exists(f"../output/from_image/{t_date}"):
        os.mkdir(f"../output/from_image/{t_date}")
        log_info(f"Создана папка '/output/from_image/{t_date}'")

    return f"../output/from_image/{t_date}/{t_time}.png"


def create_path_for_download_video() -> str:
    """
    Создаёт шаблон пути для видео файла, которую необходимо скачать
    :return: относительный путь к видео файлу
    """
    now_date = datetime.now().strftime('%d-%m-%Y')
    now_time = datetime.now().strftime('%H-%M-%S')

    if not os.path.exists('../download'):
        os.mkdir('../download')
        log_info("Создана папка '/download'")

    if not os.path.exists('../download/video'):
        os.mkdir('../download/video')
        log_info("Создана папка '/download/video'")

    if not os.path.exists(f'../download/video/{now_date}'):
        os.mkdir(f'../download/video/{now_date}')
        log_info(f"Создана папка '/download/video/{now_date}'")

    return f'../download/video/{now_date}/{now_time}.mp4'


def create_path_for_download_frame() -> str:
    """
    Создаёт шаблон пути для фотографии, которую необходимо обрезать из кадра
    :return: относительный путь к фотографии
    """
    now_date = datetime.now().strftime('%d-%m-%Y')
    now_time = datetime.now().strftime('%H-%M-%S')

    if not os.path.exists("../output/"):
        os.mkdir("../output/")
        log_info("Создана папка '/output'")

    if not os.path.exists("../output/from_video"):
        os.mkdir("../output/from_video")
        log_info("Создана папка '/output/from_video'")

    if not os.path.exists(f"../output/from_video/{now_date}"):
        os.mkdir(f"../output/from_video/{now_date}")
        log_info(f"Создана папка '/output/from_video/{now_date}'")

    return f'../output/from_video/{now_date}/{now_time}.png'


def create_path_for_download_frame1() -> str:
    """
    Создаёт шаблон пути для фотографии, которую необходимо обрезать из кадра
    :return: относительный путь к фотографии
    """
    now_date = datetime.now().strftime('%d-%m-%Y')
    now_time = datetime.now().strftime('%H-%M-%S')

    if not os.path.exists("download"):
        os.mkdir("download")
        log_info("Создана папка '/download'")

    if not os.path.exists('../download/frame'):
        os.mkdir('../download/frame')
        log_info("Создана папка '/download/frame'")

    if not os.path.exists(f"download/{now_date}"):
        os.mkdir(f"download/{now_date}")
        log_info(f"Создана папка '/download/frame/{now_date}'")

    return f'/download/frame/{now_date}/{now_time}.png'


def create_path_for_first_frame() -> str:
    """
    Создаёт шаблон пути для первого кадра видео файла
    :return: относительный путь к фотографии
    """
    now_date = datetime.now().strftime('%d-%m-%Y')
    now_time = datetime.now().strftime('%H-%M-%S')

    if not os.path.exists('../output'):
        os.mkdir('../output')

    if not os.path.exists('../output/from_video'):
        os.mkdir('../output/from_video')

    if not os.path.exists('../output/from_video/first_frame'):
        os.mkdir('../output/from_video/first_frame')

    return f'../output/from_video/first_frame/{now_date}_{now_time}.png'


def create_path_for_video(path_video) -> str:
    if not os.path.exists('../output'):
        os.mkdir('../output')
        log_info("Создана папка '/output'")
    if not os.path.exists('../output/video'):
        os.mkdir('../output/video')
        log_info("Создана папка '/output/video'")

    t_path = path_video.split('/')
    t_path1 = t_path[-1].split('.')

    if re.fullmatch(r'\d\d-\d\d', t_path1[0]) and t_path1[1] in ['mp4', 'mkv']:
        filename = t_path[-1]
        now_date = datetime.now().strftime('%d-%m-%Y')
    else:
        now_date = datetime.now().strftime('%d-%m-%Y')
        now_time = datetime.now().strftime('%H-%M-%S')
        filename = f"{now_time}.{t_path1[-1]}"

    if not os.path.exists(f"../output/video/{now_date}"):
        os.mkdir(f"../output/video/{now_date}")
        log_info(f"Создана папка '/output/video/{now_date}'")
        return f"../output/video/{now_date}/{filename}"

    return f"../output/video/{now_date}/{filename}"


def create_path_for_yolo(model_yolo: str) -> str:
    """
    Создаёт шаблон пути к выбранной модели yolo
    :param model_yolo: название конкретной модели yolo8: 'YOLOv8n', 'YOLOv8s', 'YOLOv8m', 'YOLOv8l', 'YOLOv8x'
    :return: путь к данной модели (все директории и сама модель будут предварительно созданы)
    """
    if not os.path.exists('../yolov8_models'):
        os.mkdir('../yolov8_models')

    return '../yolov8_models/' + model_yolo
