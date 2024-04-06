from typing import Generator, Tuple
from codePy.classes import User, Line, Point
import matplotlib.pyplot as plt
from ultralytics import YOLO
import supervision as sv
import numpy as np
import asyncio
import cv2


async def found_people_from_stream(path_video: str, user: User):
    text_point = Point(100, 100)
    start_point = Point(460, 523)
    end_point = Point(1050, 683)
    line = Line(start_point, end_point)

    yolo_path = '../yolov8_models/yolov8x.pt'
    model = YOLO(yolo_path)

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5
    )

    # generator = sv.get_video_frames_generator(path_video)
    # iterator = iter(generator)
    # frame = next(iterator)
    # show_frame(frame, (16, 16))

    for result in model.track(source=path_video,
                              stream=True,
                              show_conf=False,
                              conf=0.3,
                              vid_stride=2,
                              classes=0
                              ):

        frame = result.orig_img

        detections = sv.Detections.from_ultralytics(result)

        labels = [
            f"#{detection[4]}, {detection[2]:0.2f}"
            for detection
            in detections
        ]

        frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
        if detections.tracker_id is not None:
            if not line.is_convert:
                line.convert()
        cv2.line(frame, line.start_point.to_list(), line.end_point.to_list(), (255, 102, 102), 5)
        line.trigger(detections)
        text = f"In: {line.in_coming}\n;Out: {line.out_coming}"

        cv2.putText(frame, text, text_point.to_list(),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 102, 102), 3)

        cv2.imshow("yolov8", frame)

        if user.check_status_event():
            await user.send_message(f"{line.in_coming} человек перешли линию сверху-вниз;\n"
                                    f"{line.out_coming} человек перешли линию снизу-вверх")
            user.clear_status_event()

        if user.check_stop_event():
            print('Мы закончили')
            break

        if cv2.waitKey(30) == 27:  # Esc
            await user.send_message("Поиск остановлен из вне")
            break

    cv2.destroyAllWindows()
    user.close_bot()


def start_found_and_counting_found_people_on_stream(path: str, user: User):
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
        loop.stop()
        loop.close()
        print('Event loop закрылся')


def get_video_frames_generator(video_path: str) -> Generator[int, None, None]:
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise Exception(f"Видео {video_path} не открыто")
    success, frame = video.read()
    while success:
        yield frame
        success, frame = video.read()
    video.release()


def show_frame(frame: np.ndarray, size: Tuple[int, int] = (10, 10), cmap: str = "gray"):
    if frame.ndim == 2:
        plt.figure(figsize=size)
        plt.imshow(frame, cmap=cmap)
    else:
        plt.figure(figsize=size)
        plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.show()
