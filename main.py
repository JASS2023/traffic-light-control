import RPi.GPIO as GPIO
from time import sleep

def turn_on_led(gpio_num: int, duration: float = 3):
    """Turn on the LED for a given gpio pin"""
    GPIO.output(gpio_num, GPIO.HIGH)
    sleep(duration)
    GPIO.output(gpio_num, GPIO.LOW)

LED_RED_GPIO = 14
LED_YELLOW_GPIO = 18
LED_GREEN_GPIO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_GREEN_GPIO, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_RED_GPIO, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_YELLOW_GPIO, GPIO.OUT, initial=GPIO.LOW)

try:
    while True:
        turn_on_led(LED_RED_GPIO)
        sleep(1)
        turn_on_led(LED_YELLOW_GPIO)
        sleep(1)
        turn_on_led(LED_GREEN_GPIO)
        sleep(1)              
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()