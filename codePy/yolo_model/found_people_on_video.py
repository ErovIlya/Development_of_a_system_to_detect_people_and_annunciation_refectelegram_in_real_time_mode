from ultralytics import YOLO


def found_people_on_video(video_path):
    model = YOLO('../../yolov8n.pt')
    results = model.track(source=video_path, show=True, stream=True, classes=0)
    print(results)
