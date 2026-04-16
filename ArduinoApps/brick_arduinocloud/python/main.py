# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

# EXAMPLE_NAME = "Arduino Cloud LED Blink Example"
from arduino.app_bricks.arduino_cloud import ArduinoCloud
from arduino.app_utils import *
import time

# If secrets are not provided in the class initialization, they will be read from environment variables
arduino_cloud = ArduinoCloud()


def led_callback(client: object, value: bool):
    """Callback function to handle LED blink updates from cloud."""
    print(f"LED blink value updated from cloud: {value}")


arduino_cloud.register("led", value=False, on_write=led_callback)

App.start_brick(arduino_cloud)

def loop():
    Bridge.call("set_led_state", arduino_cloud.led)


App.run(user_loop=loop)