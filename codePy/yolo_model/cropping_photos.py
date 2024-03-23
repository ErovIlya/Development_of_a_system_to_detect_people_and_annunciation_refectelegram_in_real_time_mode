import datetime
import cv2
import os


def cropping_photo_from_frame(frame, xyxy):
    x1 = int(xyxy[0])
    y1 = int(xyxy[1])
    x2 = int(xyxy[2])
    y2 = int(xyxy[3])

    crop_img = frame[y1:y2, x1:x2]

    now_date = datetime.datetime.now().strftime('%d-%m-%Y')
    now_time = datetime.datetime.now().strftime('%H-%M-%S')

    if not os.path.exists("../output/"):
        os.mkdir("../output/")
    if not os.path.exists("../output/from_video"):
        os.mkdir("../output/from_video")

    if not os.path.exists(f"../output/from_video/{now_date}"):
        os.mkdir(f"../output/from_video/{now_date}")

    path = f"../output/from_video/{now_date}/{now_time}.png"
    cv2.imwrite(path, crop_img)

    return path
