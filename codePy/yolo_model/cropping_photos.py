from codePy.utils.create_path_for_files import create_path_for_download_frame
from codePy.utils.loggind_file import log_info
import numpy
import cv2


def cropping_photo_from_frame(frame: numpy.ndarray, xyxy: numpy.ndarray) -> str:
    """
    Обрезка кадра по прямоугольнику
    :param frame: кадр видео файла
    :param xyxy: координаты прямоугольника
    """
    x1 = int(xyxy[0])
    y1 = int(xyxy[1])
    x2 = int(xyxy[2])
    y2 = int(xyxy[3])

    crop_img = frame[y1:y2, x1:x2]

    path = create_path_for_download_frame()
    log_info(f"Создан файл '{path}'")
    cv2.imwrite(path, crop_img)

    return path
