# # === General imports ===
# import os
# import time
# import cv2
# from arduino.app_utils import App

# # === Brick imports ===
# from bricks.camera.camera import Camera
# from arduino.app_bricks.web_ui import WebUI

# # === Brick initialization ===
# # V4L camera at index 0
# camera = Camera(fps=30)
# camera.start()
# # Web server
# ui = WebUI()

# # === FPS tracking ===
# _fps_last_time = time.time()
# _fps_counter = 0

# # ==== Main function ====
# def streaming():
#     image = camera.capture()

#     if image is None:
#         return

#     # Atomic write: write to temp file first, then replace
#     # os.replace() is atomic on Linux — the web server always reads a complete file
#     tmp_path = "assets/latest.tmp.jpg"
#     final_path = "assets/latest.jpg"
#     cv2.imwrite(tmp_path, image)
#     os.replace(tmp_path, final_path)

#     # == FPS tracking ==
#     global _fps_last_time, _fps_counter
#     _fps_counter += 1
#     now = time.time()
#     elapsed = now - _fps_last_time
#     if elapsed >= 1.0:
#         fps = _fps_counter / elapsed
#         print(f"[FPS] latest.jpg write rate: {fps:.1f} fps")
#         _fps_counter = 0
#         _fps_last_time = now


# # Run the application
# App.run(streaming)


import time
import threading
from arduino.app_utils import App
from bricks.camera.camera import Camera
from arduino.app_bricks.web_ui import WebUI
from fastapi.responses import Response
import cv2

# ==== Camera ====
camera = Camera()
camera.start()

# ==== Thread lock ====
_frame_lock = threading.Lock()
_frame_bytes = None  

# ==== Web server ====
ui = WebUI()

def serve_latest_jpg():
    """Endpoint FastAPI : serve latest image from RAM."""
    with _frame_lock:
        data = _frame_bytes

    if data is None:
        return Response(status_code=503, content="No frame yet")

    return Response(
        content=data,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )

# Remplace le fichier statique latest.jpg par notre endpoint RAM
ui.expose_api("GET", "/latest.jpg", serve_latest_jpg)

# ==== FPS tracking ====
_fps_last_time = time.time()
_fps_counter = 0

# ==== Main: Streaming ====
def streaming():
    global _frame_bytes, _fps_last_time, _fps_counter

    image = camera.capture()
    if image is None:
        return

    # Encode in JPEG with quality 80 within RAM
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
    success, buffer = cv2.imencode(".jpg", image, encode_params)
    if not success:
        return

    # Update shared buffer thread-safe
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
