from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from datetime import datetime, UTC

# Moved brick from container to local to be able to modify it
from bricks.video_objectdetection import VideoObjectDetection

# ==== Web server ====
ui = WebUI()

# Update threshold on WebPage message (slider to update confidence threshold)
ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold)) 

# ==== Detection ====
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

# Register a callback for when any objects is detected
def send_detections_to_ui(detections: dict):
    for key, values in detections.items():
        for value in values:
            entry = {
                "content": key,
                "label": key,
                "confidence": value.get("confidence"),
                "bounding_box_xyxy": list(value.get("bounding_box_xyxy", [])),
                "track_id": value.get("track_id"),  # None if not present, JS handles it fine
                "timestamp": int(datetime.now(UTC).timestamp() * 1000)
            }
            ui.send_message("detection", message=entry)
            

detection_stream.on_detect_all(send_detections_to_ui)

App.run()