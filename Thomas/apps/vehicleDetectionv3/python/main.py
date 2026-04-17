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
TRACK_LABEL = "y"          # change if your model uses "cars" or another label
IOU_MATCH_THRESHOLD = 0.12   # how similar the new bbox must be to keep same track
TRACK_TIMEOUT_SEC = 1.0      # if not updated for this duration -> lost

# Also allow matching by center distance, not IoU only
MAX_CENTER_DISTANCE_PX = 120

# Keep a track alive longer before declaring it lost
TRACK_TIMEOUT_SEC = 2.0

# Smooth the box a bit to reduce jitter
SMOOTHING_ALPHA = 0.65

track_lock = threading.Lock()
tracked_car = None           # dict with id, bbox, confidence, last_seen
next_track_id = 1


def box_area(box):
    """Compute area of an XYXY box: (x1, y1, x2, y2)."""
    x1, y1, x2, y2 = box
    return max(0, x2 - x1) * max(0, y2 - y1)

def center_of_box(box):
    """Return the center (cx, cy) of an XYXY box."""
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

def center_distance(box_a, box_b):
    """Euclidean distance between the centers of two boxes."""
    ax, ay = center_of_box(box_a)
    bx, by = center_of_box(box_b)
    dx = ax - bx
    dy = ay - by
    return (dx * dx + dy * dy) ** 0.5

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
    Match the current track to the next detection using:
    - IoU
    - center distance

    A candidate is accepted if:
    - IoU is decent, OR
    - the center stayed close enough

    Then we rank candidates with a combined score.
    """
    best_det = None
    best_score = -1.0

    for det in candidates:
        bbox = det.get("bounding_box_xyxy")
        if bbox is None:
            continue

        iou = iou_xyxy(previous_bbox, bbox)
        dist = center_distance(previous_bbox, bbox)

        # Normalize distance to [0, 1] score
        distance_score = max(0.0, 1.0 - (dist / MAX_CENTER_DISTANCE_PX))

        # Combined score: IoU matters more, distance still helps a lot
        score = (0.7 * iou) + (0.3 * distance_score)

        # Accept if either condition says "likely same object"
        is_valid_match = (iou >= IOU_MATCH_THRESHOLD) or (dist <= MAX_CENTER_DISTANCE_PX)

        if is_valid_match and score > best_score:
            best_score = score
            best_det = det

    return best_det, best_score


def send_track_to_ui(track):
    """
    Send the tracked car to the frontend.
    The frontend will draw only a dot + the ID.
    """
    x1, y1, x2, y2 = track["bbox"]
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    ui.send_message("track", message={
        "id": track["id"],
        "label": TRACK_LABEL,
        "confidence": track["confidence"],
        "bbox": [x1, y1, x2, y2],
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

def smooth_box(old_box, new_box, alpha=SMOOTHING_ALPHA):
    """
    Smooth the tracked box to reduce visible jitter.
    alpha closer to 1.0 = more stability, less reactivity.
    """
    return (
        int(alpha * old_box[0] + (1.0 - alpha) * new_box[0]),
        int(alpha * old_box[1] + (1.0 - alpha) * new_box[1]),
        int(alpha * old_box[2] + (1.0 - alpha) * new_box[2]),
        int(alpha * old_box[3] + (1.0 - alpha) * new_box[3]),
    )


def pick_initial_target(candidates):
    """
    When no track exists, pick the largest detected object.
    This is often more stable than picking the highest confidence only.
    """
    valid = [d for d in candidates if d.get("bounding_box_xyxy") is not None]
    if not valid:
        return None
    return max(valid, key=lambda d: box_area(d["bounding_box_xyxy"]))


def update_tracking_with_detections(detections: dict):
    """
    Single-object tracking-by-detection.

    - If no track exists: pick one car and start tracking it
    - If a track exists: find the best matching car
    - If no match this frame: do not kill immediately, let the watchdog decide
    """
    global tracked_car, next_track_id

    car_detections = detections.get(TRACK_LABEL, [])
    if not car_detections:
        return

    now = time.time()

    with track_lock:
        # Start a new track if none exists
        if tracked_car is None:
            best = pick_initial_target(car_detections)
            if best is None:
                return

            tracked_car = {
                "id": next_track_id,
                "bbox": tuple(best["bounding_box_xyxy"]),
                "confidence": best.get("confidence", 0.0),
                "last_seen": now,
            }
            next_track_id += 1
            send_track_to_ui(tracked_car)
            return

        # Try to match the current track to one of the new detections
        best_match, best_score = choose_best_match(tracked_car["bbox"], car_detections)

        if best_match is not None:
            new_bbox = tuple(best_match["bounding_box_xyxy"])

            # Smooth the box so the center dot jitters less
            tracked_car["bbox"] = smooth_box(tracked_car["bbox"], new_bbox)
            tracked_car["confidence"] = best_match.get("confidence", 0.0)
            tracked_car["last_seen"] = now

            send_track_to_ui(tracked_car)
            return

        # No good match this frame:
        # do nothing here; the watchdog thread will clear stale tracks later

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