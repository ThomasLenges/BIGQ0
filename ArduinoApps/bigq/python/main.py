from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from cameraStreaming import get_frame

ui = WebUI()

ui.expose_api("GET", "/frame.jpg", get_frame)

ui.start() # Start the web server


App.run()
