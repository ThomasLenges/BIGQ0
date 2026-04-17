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
 
# ==== Face detector (built into OpenCV, no model to download) ====
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
 
# ==== Main: Streaming + Face Detection ====
def streaming():
    global _frame_bytes, _fps_last_time, _fps_counter
 
    image = camera.capture()
    if image is None:
        return
    
    # === Face detection pipeline ===
    # 1. Convert to grayscale for detection (faster, more accurate)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. Detect faces
    # scaleFactor=1.1 : checks at multiple scales (zoom levels)
    # minNeighbors=5  : how many detections needed to confirm a face (higher = less false positives)
    # minSize=(60,60) : ignore faces smaller than 60x60 pixels
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    
    # 3. Draw a rectangle around each detected face
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)
        cv2.putText(image, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
 
    # 4. Encode and store in RAM
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
    success, buffer = cv2.imencode(".jpg", image, encode_params)
    if not success:
        return
 
    with _frame_lock:
        _frame_bytes = buffer.tobytes()
 
    # FPS counter
    _fps_counter += 1
    now = time.time()
    elapsed = now - _fps_last_time
    if elapsed >= 1.0:
        fps = _fps_counter / elapsed
        print(f"[FPS] write rate: {fps:.1f} fps")
        _fps_counter = 0
        _fps_last_time = now
 
 
App.run(streaming)