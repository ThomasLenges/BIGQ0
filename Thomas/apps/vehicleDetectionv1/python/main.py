from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC

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
        "confidence": value.get("confidence"),
        "timestamp": datetime.now(UTC).isoformat()
      }
      ui.send_message("detection", message=entry)

detection_stream.on_detect_all(send_detections_to_ui)

App.run()