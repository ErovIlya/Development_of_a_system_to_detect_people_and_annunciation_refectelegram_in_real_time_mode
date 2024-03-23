from ultralytics import YOLO
import cv2
import os


def found_people_on_photo(img_path, now_date, now_time):
    yolo_path = 'yolov8_models/yolov8m.pt'
    if not os.path.exists(yolo_path):
        print(f"Не найден необходимый модуль {yolo_path}\nСейчас начнётся загрузка")
    model = YOLO(yolo_path)
    img = cv2.imread(img_path)

    results = model.predict(source=img, show_conf=True, classes=0)
    boxes = results[0].boxes.xywh

    res_img = results[0].plot()

    if not os.path.exists('../output'):
        os.mkdir('../output')
    if not os.path.exists('../output/from_image'):
        os.mkdir('../output/from_image')
    if not os.path.exists(f"../output/from_image/{now_date}"):
        os.mkdir(f"../output/from_image/{now_date}")

    path = f"../output/from_image/{now_date}/{now_time}.png"
    cv2.imwrite(path, res_img)

    rows, columns = boxes.shape
    result_str = f"Найдено {rows} человек на данном фото\nРезультат сохранён в {path}"
    return result_str, path
