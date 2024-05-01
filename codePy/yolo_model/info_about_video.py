import datetime
import cv2
import os


def get_first_frame(path_video: str, start_point: [int, int], end_point: [int, int]) -> str:
    video = cv2.VideoCapture(path_video)
    success, frame = video.read()

    if not os.path.exists('../output'):
        os.mkdir('../output')
    if not os.path.exists('../output/from_video'):
        os.mkdir('../output/from_video')
    if not os.path.exists('../output/from_video/first_frame'):
        os.mkdir('../output/from_video/first_frame')

    now_date = datetime.datetime.now().strftime('%d-%m-%Y')
    now_time = datetime.datetime.now().strftime('%H-%M-%S')
    path = f"../output/from_video/first_frame/{now_date}_{now_time}.png"

    if success:
        cv2.line(frame, start_point, end_point, (255, 102, 102), 5)
        cv2.imwrite(path, frame)
    else:
        path = '../input/image/default.png'
    return path


def get_size_frame(path_video: str) -> [int, int]:
    video = cv2.VideoCapture(path_video)
    success, frame = video.read()

    if success:
        w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return [w, h]
    else:
        return [0, 0]
