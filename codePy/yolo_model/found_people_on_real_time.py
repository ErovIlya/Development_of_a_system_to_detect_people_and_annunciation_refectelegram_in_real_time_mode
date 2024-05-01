from codePy.yolo_model.cropping_photos import cropping_photo_from_frame
from codePy.classes import User, StateForTask1
from ultralytics import YOLO
import supervision as sv
import numpy as np
import datetime
import asyncio
import cv2
import os


LIST_ALL_TRACKER_ID = {}
LIST_TEMP_TRACKER_ID = []
YOLO_PATH = '../yolov8_models/yolov8m.pt'
MODEL = YOLO(YOLO_PATH)
BYTE_TRACKER = sv.ByteTrack(track_thresh=0.25, track_buffer=30, match_thresh=0.8, frame_rate=30)
box_annotator = sv.BoxAnnotator(
    thickness=2,
    text_thickness=1,
    text_scale=0.5
)


async def found_people_from_stream(path_video: str, user: User) -> None:

    await user.send_message("Поиск начался")

    list_tracker_id = []  # Список трекеров, которые были обнаружены на кадре

    for result in MODEL.track(source=path_video,
                              stream=True,
                              # persist=True,
                              show_conf=False,
                              conf=0.3,
                              # show=True,
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
            now_date = datetime.datetime.now().strftime('%d-%m-%Y')
            now_time = datetime.datetime.now().strftime('%H-%M-%S')

            if not os.path.exists("download"):
                os.mkdir("download")

            if not os.path.exists(f"download/{now_date}"):
                os.mkdir(f"download/{now_date}")

            path = f"download/{now_date}/{now_time}.png"
            cv2.imwrite(path, frame)
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
    await user.close_bot()


def callback(frame: np.ndarray, index: int):
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


async def download_video_task1(path_input_video: str, path_output_video: str, user: User):
    await user.send_message("Скачивание видео началось")
    sv.process_video(
        source_path=path_input_video,
        target_path=path_output_video,
        callback=callback
    )
    await user.send_message("Скачивание видео завершилось")


def start_found_people_on_stream(path: str, user: User, state: int) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if state == StateForTask1.stream():
            loop.run_until_complete(found_people_from_stream(path, user))
        elif state == StateForTask1.search():
            loop.run_until_complete(download_video_task1(path,
                                                         '../output/video/video_result_task_1.mkv', user))
    except asyncio.TimeoutError:
        loop.call_soon_threadsafe(
            asyncio.create_task,
            print(f"{user.chat_id}, Непредвиденная ошибка")
        )
    finally:
        loop.stop()     # Сделать, чтобы статус у человека менялся, если видео заканчивается или его кто-то закрывает
        loop.close()
        print('Event loop закрылся')
