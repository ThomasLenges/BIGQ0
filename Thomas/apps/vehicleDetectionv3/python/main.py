from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from datetime import datetime, UTC

# Moved brick from container to local to be able to modify it
from bricks.video_objectdetection import VideoObjectDetection

import threading
import time

# ==== Web server ====
ui = WebUI()

# ==== Detection ====
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

# Update threshold from webpage slider
ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

# =========================
# Tracking state
# =========================
TRACK_LABEL = "car"          # change if your model uses "cars" or another label
IOU_MATCH_THRESHOLD = 0.25   # how similar the new bbox must be to keep same track
TRACK_TIMEOUT_SEC = 1.0      # if not updated for this duration -> lost

track_lock = threading.Lock()
tracked_car = None           # dict with id, bbox, confidence, last_seen
next_track_id = 1


def box_area(box):
    """Compute area of an XYXY box: (x1, y1, x2, y2)."""
    x1, y1, x2, y2 = box
    return max(0, x2 - x1) * max(0, y2 - y1)


def iou_xyxy(box_a, box_b):
    """Intersection over Union for two XYXY boxes."""
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    union_area = box_area(box_a) + box_area(box_b) - inter_area
    if union_area <= 0:
        return 0.0

    return inter_area / union_area


def choose_best_match(previous_bbox, candidates):
    """
    Among detected cars, choose the one that best matches the current track.
    Each candidate is expected to contain:
      {
        "confidence": ...,
        "bounding_box_xyxy": (x1, y1, x2, y2)
      }
    """
    best_det = None
    best_score = -1.0

    for det in candidates:
        bbox = det.get("bounding_box_xyxy")
        if bbox is None:
            continue

        score = iou_xyxy(previous_bbox, bbox)
        if score > best_score:
            best_score = score
            best_det = det

    return best_det, best_score


def send_track_to_ui(track):
    x1, y1, x2, y2 = track["bbox"]
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    ui.send_message("track", message={
        "id": track["id"],
        "label": TRACK_LABEL,
        "confidence": track["confidence"],
        "bbox": track["bbox"],      # [x1, y1, x2, y2]
        "center_x": center_x,
        "center_y": center_y,
        "timestamp": datetime.now(UTC).isoformat()
    })


def send_track_lost_to_ui(track_id):
    """Notify frontend that the tracked object was lost."""
    ui.send_message("track_lost", message={
        "id": track_id,
        "timestamp": datetime.now(UTC).isoformat()
    })


def update_tracking_with_detections(detections: dict):
    """
    Tracking-by-detection:
    - if no track exists, pick the best car
    - if a track exists, keep the car with highest IoU to previous bbox
    """
    global tracked_car, next_track_id

    car_detections = detections.get(TRACK_LABEL, [])
    if not car_detections:
        return

    now = time.time()

    with track_lock:
        # Start tracking if nothing is tracked yet
        if tracked_car is None:
            best = max(car_detections, key=lambda d: d.get("confidence", 0.0))
            tracked_car = {
                "id": next_track_id,
                "bbox": best["bounding_box_xyxy"],
                "confidence": best.get("confidence", 0.0),
                "last_seen": now,
            }
            next_track_id += 1
            send_track_to_ui(tracked_car)
            return

        # Try to keep the current track alive with the best matching bbox
        best_match, best_iou = choose_best_match(tracked_car["bbox"], car_detections)

        if best_match is not None and best_iou >= IOU_MATCH_THRESHOLD:
            tracked_car["bbox"] = best_match["bounding_box_xyxy"]
            tracked_car["confidence"] = best_match.get("confidence", 0.0)
            tracked_car["last_seen"] = now
            send_track_to_ui(tracked_car)
            return

        # No good match this frame:
        # do nothing here; the watchdog below will decide when the track is really lost.


def track_watchdog():
    """
    Because the brick only calls on_detect_all when detections exist,
    we need a small watchdog to clear stale tracks ourselves.
    """
    global tracked_car

    while True:
        time.sleep(0.2)

        with track_lock:
            if tracked_car is None:
                continue

            age = time.time() - tracked_car["last_seen"]
            if age > TRACK_TIMEOUT_SEC:
                lost_id = tracked_car["id"]
                tracked_car = None
                send_track_lost_to_ui(lost_id)


# Register a callback for all detected objects
def send_detections_to_ui(detections: dict):
    # Keep your existing UI messages
    for key, values in detections.items():
        for value in values:
            entry = {
                "content": key,
                "confidence": value.get("confidence"),
                "bbox": value.get("bounding_box_xyxy"),  # useful for custom frontend overlays
                "timestamp": datetime.now(UTC).isoformat()
            }
            ui.send_message("detection", message=entry)

    # New: update tracker
    update_tracking_with_detections(detections)


detection_stream.on_detect_all(send_detections_to_ui)

# Start watchdog thread
threading.Thread(target=track_watchdog, daemon=True).start()

App.run()