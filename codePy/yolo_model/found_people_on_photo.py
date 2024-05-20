from codePy.utils.create_path_for_files import create_path_for_image, create_path_for_yolo
from ultralytics import YOLO
import cv2


def found_people_on_photo(img_path: str) -> [str, str]:
    """
    Поиск людей на фотографии
    :param img_path: относительный путь к фотографии
    :return: кортеж из двух элементов: первый - результирующая строка,
    второй - относительный путь к преобразованной фотографии
    """
    yolo_path = create_path_for_yolo('yolov8m.pt')
    model = YOLO(yolo_path)
    img = cv2.imread(img_path)

    results = model.predict(source=img, show_conf=True, classes=0)
    boxes = results[0].boxes.xywh

    res_img = results[0].plot()

    path = create_path_for_image(img_path)
    cv2.imwrite(path, res_img)

    rows, columns = boxes.shape
    result_str = f"Найдено {rows} человек на данном фото\nРезультат сохранён в {path}"
    return result_str, path
