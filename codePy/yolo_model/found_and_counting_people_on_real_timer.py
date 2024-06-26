from codePy.utils.create_path_for_files import create_path_for_yolo, create_path_for_video
from codePy.utils.unload_files_on_cloud import unload_file_in_cloud, create_dir_in_cloud
from codePy.utils.line_counter import (Point,
                                       WhichPointObjectBeTracked)
from codePy.yolo_model.info_about_video import get_size_frame
from codePy.utils.line_counter import Line, LineBoxAnnotated
from codePy.utils.zone_counted import Zone, ZoneBoxAnnotated
from codePy.utils.classes import User, StateForTask2
from codePy.utils.classes import FPSBaseTimer
import codePy.utils.database as db
from functools import partial
from ultralytics import YOLO
from operator import is_not
import supervision as sv
import numpy as np
import asyncio
import cv2


GLOBAL_LINE = Line(Point(0, 0), Point(1000, 1000))
GLOBAL_ZONE = Zone([Point(0, 0), Point(0, 0), Point(0, 0)])

BYTE_TRACKER = sv.ByteTrack()
YOLO_PATH = create_path_for_yolo('yolov9e.pt')
MODEL = YOLO(YOLO_PATH)

TIMER = FPSBaseTimer()

TRACE_ANNOTATOR = sv.TraceAnnotator(thickness=4, trace_length=50)   # Рисует траектории движения для каждого обнаружения
BOUNDING_BOX_ANNOTATOR = sv.BoundingBoxAnnotator()  # Рисует ограничивающие рамки для каждого обнаружения
LABEL_ANNOTATOR = sv.LabelAnnotator()   # Рисует метки для каждого обнаружения


def create_timer(path: str) -> None:
    """
    Обёртка для создания Таймера
    :param path: путь к видео файлу
    """
    video_info = sv.VideoInfo.from_video_path(path)
    global TIMER
    TIMER = FPSBaseTimer(video_info.fps)


def read_from_db_line_and_zone(chat_id: int) -> None:
    """
    Чтение введённых данных из БД
    :param chat_id: ID чата/пользователя
    """
    db_line = db.get_line(chat_id)
    db_zone = db.get_zone(chat_id)
    db_sp_point = db.get_sp_point(chat_id)

    db_path = db.get_video_path(chat_id)
    path = db_path if db_path is not None else '../input/video/video_task_2.mkv'
    width, height = get_size_frame(path)

    if db_sp_point is None:
        db_sp_point = WhichPointObjectBeTracked.center()

    if db_line is None:
        point_start = Point(0, 0)
        point_end = Point(width, height)
    else:
        point_start = Point(db_line[1], db_line[2])
        point_end = Point(db_line[3], db_line[4])
    global GLOBAL_LINE
    GLOBAL_LINE = Line(point_start, point_end, db_sp_point)
    
    if db_zone is None:
        point1 = Point(0, 0)
        point2 = Point(width, 0)
        point3 = Point(width, height)
        point4 = Point(0, height)
        point5 = Point(0, 0)
    else:
        db_zone = list(filter(partial(is_not, None), db_zone))
        point1 = Point(db_zone[1], db_zone[2])
        point2 = Point(db_zone[3], db_zone[4])
        point3 = Point(db_zone[5], db_zone[6])
        if len(db_zone) > 7:
            point4 = Point(db_zone[7], db_zone[8])
        else:
            point4 = None
        if len(db_zone) > 9:
            point5 = Point(db_zone[9], db_zone[10])
        else:
            point5 = None
    zone = Zone([point1, point2, point3, point4, point5], db_sp_point)
    global GLOBAL_ZONE
    GLOBAL_ZONE = zone


async def found_people_from_stream(user: User) -> None:
    """
    Выполнение задачи 2 в режиме реального времени
    :param user: объект класса User
    """
    read_from_db_line_and_zone(user.chat_id)
    db_path = db.get_video_path(user.chat_id)
    path_video = db_path if db_path is not None else '../input/video/video_task_2.mkv'
    create_timer(path_video)
    cap = cv2.VideoCapture(path_video)

    if not cap.isOpened():
        await user.send_message("Не удалось открыть видео")
        return

    while True:
        success, frame = cap.read()
        new_frame = callback(frame, 0)
        cv2.imshow("yolov8", new_frame)

        if user.check_status_event():
            await user.send_message(f"{GLOBAL_LINE.in_count} "
                                    f"человек перешли линию сверху-вниз;\n"
                                    f"{GLOBAL_LINE.out_count} человек перешли линию снизу-вверх")
            user.clear_status_event()

        if user.check_stop_event():
            print('Мы закончили')
            break

        if cv2.waitKey(30) == 27 or not success:  # Esc
            await user.send_message("Поиск остановлен из вне")
            break

    cv2.destroyAllWindows()
    await user.clear_status()
    await user.close_bot()


async def download_video_task2(user: User) -> None:
    """
    Выполнение задачи 2 и преобразование его в выходной видеофайл
    :param user: объект класса User
    """
    db_path = db.get_video_path(user.chat_id)
    path_video = db_path if db_path is not None else '../input/video/video_task_2.mkv'
    read_from_db_line_and_zone(user.chat_id)
    path_out = create_path_for_video(path_video)
    remote_path = create_dir_in_cloud(path_out)

    await user.send_message("Обработка видео началась")
    sv.process_video(
        source_path=path_video,
        target_path=path_out,
        callback=callback
    )

    await user.send_message("Обработка видео завершилась\nНачалась выгрузка видео в облако")
    remote = unload_file_in_cloud(path_out, remote_path)
    await user.send_message(f"Файл выгружен на облако\nОтносительный путь к файлу на облаке: '{remote}'\n"
                            f"Ссылка на облако: https://cloud.mail.ru/public/EC3d/QrxFXCNP1")
    await user.clear_status()


def callback(frame: np.ndarray, index: int) -> np.ndarray:
    results = MODEL(frame, verbose=False, classes=0, show_conf=False, conf=0.3)[0]

    detections = sv.Detections.from_ultralytics(results)
    detections = BYTE_TRACKER.update_with_detections(detections)

    object_in_zone = GLOBAL_ZONE.trigger(detections)
    detections_in_zone = detections[object_in_zone]

    if detections_in_zone.tracker_id is None:
        detections_in_zone.tracker_id = np.array([])

    times = TIMER.tick(detections_in_zone)
    labels = [
        f"#{tracker_id}, {time:.1f}s"
        for tracker_id, time
        in zip(detections_in_zone.tracker_id, times)
    ]

    annotated_frame = TRACE_ANNOTATOR.annotate(
        scene=frame.copy(),
        detections=detections_in_zone
    )
    annotated_frame = BOUNDING_BOX_ANNOTATOR.annotate(
        scene=annotated_frame,
        detections=detections_in_zone
    )
    annotated_frame = LABEL_ANNOTATOR.annotate(
        scene=annotated_frame,
        detections=detections_in_zone,
        labels=labels
    )

    if detections_in_zone.tracker_id is not None:
        GLOBAL_LINE.trigger(detections_in_zone)

    annotated_frame = ZoneBoxAnnotated.annotate(frame=annotated_frame, zone=GLOBAL_ZONE, color=(0, 0, 255))
    return LineBoxAnnotated.annotate(frame=annotated_frame, line=GLOBAL_LINE, color=(0, 165, 255))


def start_execution_task2(user: User, state: int) -> None:
    """
    Начало выполнения задачи2
    :param user: объект класса User
    :param state: номер подзадачи
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if state == StateForTask2.stream():
            loop.run_until_complete(found_people_from_stream(user))
        elif state == StateForTask2.search():
            loop.run_until_complete(download_video_task2(user))
    except asyncio.TimeoutError:
        loop.call_soon_threadsafe(
            asyncio.create_task,
            user.send_message("Непредвиденная ошибка в потоке")
        )
    finally:
        loop.stop()
        loop.close()
        print('Event loop закрылся')
