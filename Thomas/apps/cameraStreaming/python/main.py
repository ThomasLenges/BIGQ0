import os
from arduino.app_utils import App
from bricks.camera.camera import Camera

#from bricks.web_ui.web_ui import WebUI
from arduino.app_bricks.web_ui import WebUI
import cv2

# V4L camera at index 0
camera = Camera()
camera.start()

# Web server
ui = WebUI()

def streaming():
    image = camera.capture()

    if image is None:
        return

    cv2.imwrite("assets/latest.jpg", image)


# Run the application
App.run(streaming)