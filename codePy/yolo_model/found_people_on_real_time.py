from codePy.yolo_model.cropping_photos import cropping_photo_from_frame, download_frame
from codePy.classes import User
from ultralytics import YOLO
import supervision as sv
import datetime
import asyncio
import time
import cv2
import os


list_all_tracker_id = {}


async def found_people_from_stream(path_video: str, user: User):
    yolo_path = '../yolov8_models/yolov8m.pt'
    model = YOLO(yolo_path)

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5
    )

    await user.send_message("Поиск начался")

    list_tracker_id = []  # Список трекеров, которые были обнаружены на кадре

    for result in model.track(source=path_video,
                              stream=True,
                              # persist=True,
                              show_conf=False,
                              conf=0.3,
                              # show=True,
                              vid_stride=2,
                              classes=0
                              ):

        start = time.perf_counter()
        frame = result.orig_img
        detections = sv.Detections.from_ultralytics(result)

        # Если нет обнаружений, то скрипт ломается, поэтому необходимо это предотвратить следующими 2 строками
        if result.boxes.id is not None:
            detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)

        if detections.tracker_id is not None:
            list_tracker_id = detections.tracker_id.flatten()
            j = 0
            for temp_tracker_id in list_tracker_id:
                if temp_tracker_id not in list_all_tracker_id:    # Если его нет среди обнаруженных
                    list_all_tracker_id[temp_tracker_id] = True
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

        if cv2.waitKey(30) == 27:   # Esc
            await user.send_message("Поиск остановлен из вне")
            break

        end = time.perf_counter()

        print(f"Выполнение кода составило - {end - start}")

    cv2.destroyAllWindows()
    list_all_tracker_id.clear()
    user.close_bot()


def start_found_people_on_stream(path: str, user: User):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(found_people_from_stream(path, user))
    except asyncio.TimeoutError:
        loop.call_soon_threadsafe(
            asyncio.create_task,
            print(f"{user.chat_id}, Непредвиденная ошибка")
        )
    finally:
        loop.stop()     # Сделать, чтобы статус у человека менялся, если видео заканчивается или его кто-то закрывает
        loop.close()
        print('Event loop закрылся')
