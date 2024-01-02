from codePy.telegram_bot.create_bot import TOKEN_API
from codePy.yolo_model.cropping_photos import cropping_photo_from_frame
from aiogram.types import InputFile
from ultralytics import YOLO
import supervision as sv
from aiogram import Bot
import datetime
import asyncio
import time
import cv2
import os


# list_tracker_id_on_frame = {}
list_all_tracker_id = {}
bot = Bot(TOKEN_API)


async def send_message_from_stream(chat_id, text):
    await bot.send_message(chat_id, text)


async def send_photo_from_stream(chat_id, path, text):
    photo = InputFile(path)
    await bot.send_photo(chat_id, photo, caption=text)


async def found_people_from_stream(path_video, chat_id, stop_event, status_event):
    yolo_path = 'yolov8_models/yolov8l.pt'
    model = YOLO(yolo_path)

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5
    )

    await send_message_from_stream(chat_id, "Поиск начался")

    for result in model.track(source=path_video,
                              stream=True,
                              # persist=True,
                              show_conf=False,
                              # show=True,
                              vid_stride=2,
                              classes=0
                              ):

        start = time.perf_counter()
        frame = result.orig_img
        detections = sv.Detections.from_yolov8(result)
        """
            Если нет обнаружений, то скрипт ломается, поэтому необходимо это предотвратить следующими 2 строками
        """
        if result.boxes.id is not None:
            detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)

        global list_tracker_id_on_frame
        list_tracker_id = []    # Список трекеров, которые были обнаружена на старом кадре

        if detections.tracker_id is not None:
            list_tracker_id = detections.tracker_id.flatten()
            j = 0
            for temp_tracker_id in list_tracker_id:
                # print(temp_tracker_id)

                if temp_tracker_id not in list_all_tracker_id:    # Если его нет на старом кадре
                    list_all_tracker_id[temp_tracker_id] = True
                    print(f"Новый человек на кадре: {temp_tracker_id}")
                    print(f"{detections.xyxy[j]}")

                    path = cropping_photo_from_frame(frame, detections.xyxy[j])
                    await send_photo_from_stream(chat_id, path, 'Найден данный человек на записи')
                j += 1

        labels = [
            f"#{tracker_id} {model.model.names[class_id]} {confidence:0.2f}"
            for _, _, confidence, class_id, tracker_id
            in detections
        ]

        frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

        cv2.imshow("yolov8", frame)

        if status_event.is_set():
            now_date = datetime.datetime.now().strftime('%d-%m-%Y')
            now_time = datetime.datetime.now().strftime('%H-%M-%S')

            if not os.path.exists("download"):
                os.mkdir("download")

            if not os.path.exists(f"download/{now_date}"):
                os.mkdir(f"download/{now_date}")

            path = f"download/{now_date}/{now_time}.png"
            cv2.imwrite(path, frame)
            await send_photo_from_stream(chat_id, path, f"Сейчас на кадре {len(list_tracker_id)} человек")
            status_event.clear()

        if stop_event.is_set():
            print('Мы закончили')
            break

        if cv2.waitKey(30) == 27:   # Esc
            await send_message_from_stream(chat_id, "Поиск остановлен из вне")
            break

        end = time.perf_counter()

        print(f"Выполнение кода составило - {end - start}")

    cv2.destroyAllWindows()
    list_all_tracker_id.clear()


def start_found_people_on_stream(path, chat_id, stop_event, status_event):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(found_people_from_stream(path, chat_id, stop_event, status_event))
    except asyncio.TimeoutError:
        loop.call_soon_threadsafe(
            asyncio.create_task,
            print(f"{chat_id}, Непредвиденная ошибка")
        )
    else:
        loop.call_soon_threadsafe(
            asyncio.create_task,
            print(f"{chat_id}, Задание выполнено")
        )
    finally:
        loop.stop()
        print('Event loop закрылся')
