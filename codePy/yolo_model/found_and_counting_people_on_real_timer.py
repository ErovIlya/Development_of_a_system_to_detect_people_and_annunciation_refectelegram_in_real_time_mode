from codePy.classes import User, Line, Point, StateForTask2
from codePy.unload_video import unload_file_in_cloud
from ultralytics import YOLO
import supervision as sv
import numpy as np
import asyncio
import cv2


TEXT_POINT = Point(100, 100)  # Point(100, 100)
GLOBAL_LINE = sv.LineZone(sv.Point(0, 0), sv.Point(1000, 1000))

LIST_POINTS = []

BYTE_TRACKER = sv.ByteTrack(track_thresh=0.25, track_buffer=30, match_thresh=0.8, frame_rate=30)
YOLO_PATH = '../yolov8_models/yolov8x.pt'
MODEL = YOLO(YOLO_PATH)

# create instance of TraceAnnotator
trace_annotator = sv.TraceAnnotator(thickness=4, trace_length=50)

# create LineZoneAnnotator instance, it is previously called LineCounterAnnotator class
line_zone_annotator = sv.LineZoneAnnotator(thickness=4, text_thickness=4, text_scale=2)


def create_line(line: sv.LineZone = None) -> None:
    if line is None:
        start_point = sv.Point(460, 523)  # Point(460, 523)
        end_point = sv.Point(1050, 683)
        # line = Line(start_point, end_point)
        line = sv.LineZone(start=start_point, end=end_point)

    global GLOBAL_LINE
    GLOBAL_LINE = line


async def found_people_from_stream(path_video: str, user: User, line: sv.LineZone = None) -> None:
    create_line(line)
    cap = cv2.VideoCapture(path_video)
    if not cap.isOpened():
        await user.send_message("Не удалось открыть видео")
        return

    while True:  # Измерить время выполнения до и псоле изменения
        success, frame = cap.read()
        new_frame = callback(frame, 0)
        cv2.imshow("yolov8", new_frame)

        if user.check_status_event():
            await user.send_message(f"{GLOBAL_LINE.in_count} человек перешли линию сверху-вниз;\n"
                                    f"{GLOBAL_LINE.out_count} человек перешли линию снизу-вверх")
            user.clear_status_event()

        if user.check_stop_event():
            print('Мы закончили')
            break

        if cv2.waitKey(30) == 27 or not success:  # Esc
            await user.send_message("Поиск остановлен из вне")
            break

    cv2.destroyAllWindows()
    await user.close_bot()


async def download_video_task2(path_input_video: str, path_output_video: str, user: User, line: sv.LineZone) -> None:
    create_line(line)
    
    await user.send_message("Обработка видео началась")
    sv.process_video(
        source_path=path_input_video,
        target_path=path_output_video,
        callback=callback
    )
    await user.send_message("Обработка видео завершилось\nНачалась выгрузка видео в облако")
    unload_file_in_cloud(path_output_video)
    await user.send_message("Файл выгружен на облако")


def callback(frame: np.ndarray, index: int):
    results = MODEL(frame, verbose=False, classes=0, show_conf=False, conf=0.3)[0]

    detections = sv.Detections.from_ultralytics(results)
    detections = BYTE_TRACKER.update_with_detections(detections)
    labels = [
        f"#{detection[4]}, {detection[2]:0.2f}"
        for detection
        in detections
    ]
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5
    )

    # frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
    annotated_frame = trace_annotator.annotate(
        scene=frame.copy(),
        detections=detections
    )
    annotated_frame = box_annotator.annotate(
        scene=annotated_frame,
        detections=detections,
        labels=labels)
    if detections.tracker_id is not None:
        # LINE.trigger(detections)
        GLOBAL_LINE.trigger(detections)

    # cv2.line(frame, LINE.start_point.to_list(), LINE.end_point.to_list(), (255, 102, 102), 5)
    # text = f"In: {LINE.in_coming}; Out: {LINE.out_coming}"

    # cv2.putText(frame, text, TEXT_POINT.to_list(),
    #             cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 0, 0), 3)

    # return frame
    return line_zone_annotator.annotate(annotated_frame, line_counter=GLOBAL_LINE)


def start_execution_task2(path: str, user: User, state: int, line: sv.LineZone = None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if state == StateForTask2.stream():
            loop.run_until_complete(found_people_from_stream(path, user, line))
        elif state == StateForTask2.search():
            str_path = path.split('/')
            new_path = '../output/video/' + str_path[-1]

            loop.run_until_complete(download_video_task2(path,
                                                         new_path, user, line))
    except asyncio.TimeoutError:
        loop.call_soon_threadsafe(
            asyncio.create_task,
            print(f"{user.chat_id}, Непредвиденная ошибка")
        )
    finally:
        loop.stop()
        loop.close()
        print('Event loop закрылся')
