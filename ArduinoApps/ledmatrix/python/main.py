import time

from arduino.app_utils import App, Leds

LED1_R = "/sys/class/leds/red:user/brightness"
LED1_G = "/sys/class/leds/green:user/brightness"
LED1_B = "/sys/class/leds/blue:user/brightness"

LED2_R = "/sys/class/leds/red:panic/brightness"
LED2_G = "/sys/class/leds/green:wlan/brightness"
LED2_B = "/sys/class/leds/blue:bt/brightness"

def set_led_brightness(led_file, value):
    try:
        with open(led_file, "w") as f:
            f.write(f"{value}\n")
    except Exception as e:
        print(f"Error writing to {led_file}: {e}")

# turn off all LEDs
set_led_brightness(LED1_R, 0)
set_led_brightness(LED1_G, 0)
set_led_brightness(LED1_B, 0)
set_led_brightness(LED2_R, 0)
set_led_brightness(LED2_G, 0)
set_led_brightness(LED2_B, 0)

def loop():
    #blink the LED 1 RED segment
    set_led_brightness(LED1_R, 1)
    Leds.set_led2_color(1,1,1) # Integrated module "Leds"
    time.sleep(1)
    set_led_brightness(LED1_R, 0)
    Leds.set_led2_color(0,0,0)
    time.sleep(1)

App.run(user_loop=loop)