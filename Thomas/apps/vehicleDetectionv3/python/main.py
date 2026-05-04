from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from datetime import datetime, UTC
from sort import Sort

# Moved brick from container to local to be able to modify it
from bricks.video_objectdetection import VideoObjectDetection

# ==== Web server ====
ui = WebUI()

# Update threshold on WebPage message (slider to update confidence threshold)
ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold)) 

# ==== Detection ====
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

tracker = Sort()

def send_detections_to_ui(detections: dict):
    boxes = []
    for label, hits in detections.items():
        for h in hits:
            x1, y1, x2, y2 = h["bounding_box_xyxy"]
            boxes.append([x1, y1, x2, y2, h["confidence"]])
    
    tracked = tracker.update(np.array(boxes))
    # tracked = [[x1, y1, x2, y2, track_id], ...]
    for t in tracked:
        ui.send_message("detection", {"id": int(t[4]), "bbox": t[:4].tolist()})

detection_stream.on_detect_all(send_detections_to_ui)

App.run()



