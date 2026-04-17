import time
import threading
import cv2
from arduino.app_utils import App
from bricks.camera.camera import Camera
from arduino.app_bricks.web_ui import WebUI
from fastapi.responses import Response

# ==== Camera ====
camera = Camera(fps=30)
camera.start()

# ==== Face detector ====
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# ==== Thread lock ====
_frame_lock = threading.Lock()
_frame_bytes = None

# ==== Web server ====
ui = WebUI()

def serve_latest_jpg():
    with _frame_lock:
        data = _frame_bytes
    if data is None:
        return Response(status_code=503, content="No frame yet")
    return Response(
        content=data,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )

ui.expose_api("GET", "/latest.jpg", serve_latest_jpg)

# ==== FPS Detection ====
_fps_last_time = time.time()
_fps_counter = 0

# ==== Tracking state ====
_trackers = []          # list of active cv2 trackers
_detect_interval = 15   # re-run detector every N frames
_frame_count = 0


def create_tracker():
    """Create a MIL tracker (only one available)."""
    return cv2.TrackerMIL_create()


def run_detection(gray, frame):
    """Detect faces and initialise fresh trackers for each one."""
    global _trackers

    faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    _trackers = []
    for (x, y, w, h) in faces:
        t = create_tracker()
        t.init(frame, (x, y, w, h))   # tracker works on the colour frame
        _trackers.append(t)


# ==== Main: Streaming + Detection + Tracking ====
def streaming():
    global _frame_bytes, _fps_last_time, _fps_counter, _frame_count

    image = camera.capture()
    if image is None:
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # === Detection pass (runs every _detect_interval frames) ===
    if _frame_count % _detect_interval == 0:
        run_detection(gray, image)

    _frame_count += 1

    # === Tracking pass (runs every frame) ===
    alive = []
    for tracker in _trackers:
        ok, bbox = tracker.update(image)
        if not ok:
            continue                    # tracker lost the face — drop it
        x, y, w, h = (int(v) for v in bbox)

        # Colour shifts green→red as tracker ages between detections
        age = _frame_count % _detect_interval
        green = int(255 * (1 - age / _detect_interval))
        red   = int(255 * (age  / _detect_interval))
        color = (0, green, red)         # BGR

        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        alive.append(tracker)

    _trackers[:] = alive   # remove lost trackers in-place

    # === Encode and store in RAM ===
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
    success, buffer = cv2.imencode(".jpg", image, encode_params)
    if not success:
        return

    with _frame_lock:
        _frame_bytes = buffer.tobytes()

    # === FPS counter ===
    _fps_counter += 1
    now = time.time()
    elapsed = now - _fps_last_time
    if elapsed >= 1.0:
        fps = _fps_counter / elapsed
        print(f"[FPS] write rate: {fps:.1f} fps  |  tracking {len(_trackers)} face(s)")
        _fps_counter = 0
        _fps_last_time = now


App.run(streaming)