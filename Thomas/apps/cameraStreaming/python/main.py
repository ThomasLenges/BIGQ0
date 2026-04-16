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
    #print("streaming!")

    if image is None:
        #print("No frame received")
        return

    ok = cv2.imwrite("assets/latest.jpg", image)
    #print(f"Saved???: {ok}")


# Run the application
App.run(streaming)


# from arduino.app_utils import App
# from bricks.webServer.web_ui import WebUI

# # Initialize the Web UI server
# ui = WebUI()

# App.run()