from arduino.app_utils import App
from arduino.app_bricks.video_objectdetection import VideoObjectDetection

detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

# Register a callback for when all objects are detected
def print_detections(detections: dict):
  for key, value in detections.items():
        for detection in value:
            entry = {
                "content": key,
                "confidence": f"{round(detection.get('confidence', 0) * 100)} %"
            }
            print(entry)

detection_stream.on_detect_all(print_detections)

App.run()