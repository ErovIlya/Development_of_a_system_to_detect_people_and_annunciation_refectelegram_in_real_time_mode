from codePy.utils.create_path_for_files import (create_path_for_download_frame1, create_path_for_yolo,
                                                create_path_for_video)
from codePy.utils.unload_files_on_cloud import unload_file_in_cloud, create_dir_in_cloud
from codePy.yolo_model.cropping_photos import cropping_photo_from_frame
from codePy.telegram_bot.clear_status import clear_status
from codePy.utils.classes import User, StateForTask1
from codePy.utils.loggind_file import log_info
import codePy.utils.database as db
from ultralytics import YOLO
import supervision as sv
import numpy as np
import asyncio
import cv2


LIST_ALL_TRACKER_ID = {}
LIST_TEMP_TRACKER_ID = []
YOLO_PATH = create_path_for_yolo('yolov8m.pt')
MODEL = YOLO(YOLO_PATH)
BYTE_TRACKER = sv.ByteTrack()
box_annotator = sv.BoundingBoxAnnotator()


async def found_people_from_stream(user: User) -> None:
    """
    Выполнение задачи 1 в режиме реального времени
    :param user: объект класса User
    """
    await user.send_message("Поиск начался")
    db_path = db.get_video_path(user.chat_id)
    path_video = db_path if db_path is not None else '../input/video/video_task_2.mkv'

    list_tracker_id = []  # Список ID обнаружения, которые были обнаружены на кадре

    for result in MODEL.track(source=path_video,
                              stream=True,
                              show_conf=False,
                              conf=0.3,
                              vid_stride=2,
                              classes=0
                              ):

        frame = result.orig_img
        detections = sv.Detections.from_ultralytics(result)

        # Если нет обнаружений, то скрипт ломается, поэтому необходимо это предотвратить следующими 2 строками
        if result.boxes.id is not None:
            detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)

        if detections.tracker_id is not None:
            list_tracker_id = detections.tracker_id.flatten()
            j = 0
            for temp_tracker_id in list_tracker_id:
                if temp_tracker_id not in LIST_ALL_TRACKER_ID:  # Если его нет среди обнаруженных
                    LIST_ALL_TRACKER_ID[temp_tracker_id] = True
                    print(f"Новый человек на кадре: {temp_tracker_id}")

                    path = cropping_photo_from_frame(frame, detections.xyxy[j])
                    await user.send_photo('Найден данный человек на записи', path)
                j += 1

        labels = [
            f"#{detection[4]}, {detection[2]:0.2f}"
            for detection
            in detections
        ]

        frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

        cv2.imshow("yolov8", frame)

        if user.check_status_event():
            path = create_path_for_download_frame1()

            cv2.imwrite(path, path)
            log_info(f"Создан файл {path}")
            await user.send_photo(f"Сейчас на кадре {len(list_tracker_id)} человек", path)
            user.clear_status_event()

        if user.check_stop_event():
            print('Мы закончили')
            break

        if cv2.waitKey(30) == 27:  # Esc
            await user.send_message("Поиск остановлен из вне")
            break

    cv2.destroyAllWindows()
    LIST_ALL_TRACKER_ID.clear()
    await clear_status(user.chat_id)
    await user.close_bot()


def callback(frame: np.ndarray, index: int):
    """
    Функция, в которой происходит преобразование файла, детектирование людей
    :param frame: изначальный "голый" кадр
    :param index:
    :return:
    """
    results = MODEL(frame, verbose=False, classes=0, show_conf=False, conf=0.3)[0]

    detections = sv.Detections.from_ultralytics(results)
    detections = BYTE_TRACKER.update_with_detections(detections)

    labels = [
        f"#{detection[4]}, {detection[2]:0.2f}"
        for detection
        in detections
    ]

    annotated_frame = box_annotator.annotate(
        scene=frame,
        detections=detections,
        labels=labels)

    return annotated_frame


async def download_video_task1(user: User) -> None:
    """
    Выполнение задачи 1 в режиме реального времени
    :param user: объект класса User
    """
    db_path = db.get_video_path(user.chat_id)
    path_video = db_path if db_path is not None else '../input/video/video_task_1.mkv'
    path_out = create_path_for_video(path_video)
    remote_path = create_dir_in_cloud(path_out)

    await user.send_message("Обработка видео началось")
    sv.process_video(
        source_path=path_video,
        target_path=path_out,
        callback=callback
    )
    await user.send_message("Обработка видео завершилась\nНачалась выгрузка видео в облако")
    unload_file_in_cloud(path_out, remote_path)
    await user.send_message("Файл выгружен на облако")
    await clear_status(user.chat_id)


def start_found_people_on_stream(user: User, state: int) -> None:
    """
    Начало выполнения задачи1
    :param user: объект класса User
    :param state: номер подзадачи
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if state == StateForTask1.stream():
            loop.run_until_complete(found_people_from_stream(user))
        elif state == StateForTask1.search():
            loop.run_until_complete(download_video_task1(user))
    except asyncio.TimeoutError:
        loop.call_soon_threadsafe(
            asyncio.create_task,
            print(f"{user.chat_id}, Непредвиденная ошибка")
        )
    finally:
        loop.stop()
        loop.close()
        print('Event loop закрылся')
