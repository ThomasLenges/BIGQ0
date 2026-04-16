# ===Basic HTML example ===
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI

# Initialize the Web UI server
web_ui = WebUI()

# Add a simple REST API endpoint
web_ui.expose_api("GET", "/hello", lambda: {"message": "Hello, world!"})
# If somebdies knocks on door "/hello" then answer with "Hello, world!"
# http://172.20.10.11:7000/hello → responds {"message": "Hello, world!"}


# Start the server
web_ui.start()

# Send a message to clients over WebSocket
web_ui.send_message("hello", {"message": "Hello broski!"})
# Server sends message to all connected clients
# "hello" is the door


# The server will now serve static files and respond to /api/hello requests

App.run()