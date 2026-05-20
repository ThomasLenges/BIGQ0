from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from datetime import datetime, UTC
import numpy as np
from filterpy.kalman import KalmanFilter
from scipy.optimize import linear_sum_assignment

from bricks.video_objectdetection import VideoObjectDetection

# ==== Tracker maison avec filterpy ====
class SimpleTracker:
    def __init__(self):
        self.trackers = {}
        self.next_id = 1

    def update(self, boxes):
        results = []
        for box in boxes:
            x1, y1, x2, y2, conf = box
            tid = self.next_id
            self.next_id += 1
            results.append([x1, y1, x2, y2, tid])
        return np.array(results) if results else np.empty((0, 5))

# ==== Web server ====
ui = WebUI()
ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

# ==== Detection ====
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)
tracker = SimpleTracker()

def send_detections_to_ui(detections: dict):
    boxes = []
    for label, hits in detections.items():
        for h in hits:
            x1, y1, x2, y2 = h["bounding_box_xyxy"]
            boxes.append([x1, y1, x2, y2, h["confidence"]])

    tracked = tracker.update(np.array(boxes)) if boxes else np.empty((0, 5))
    for t in tracked:
        ui.send_message("detection", {"id": int(t[4]), "bbox": t[:4].tolist()})

detection_stream.on_detect_all(send_detections_to_ui)
App.run()