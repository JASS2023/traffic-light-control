import RPi.GPIO as GPIO
from time import sleep

def turn_on_led(*args, duration: float = 3):
    """Turn on the LED for a given gpio pin"""
    for pin in args:
        GPIO.output(pin, GPIO.HIGH)
    sleep(duration)
    for pin in args:
        GPIO.output(pin, GPIO.LOW)

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
        # Red phase
        turn_on_led(LED_RED_GPIO, duration=10)
        # Prepare green 
        turn_on_led(LED_RED_GPIO, LED_YELLOW_GPIO, duration=2)       
        # Green phase
        turn_on_led(LED_GREEN_GPIO, duration=10)   
        # Yellow phase
        turn_on_led(LED_YELLOW_GPIO, duration=2)
except KeyboardInterrupt:
    print("Stopped")
    pass
finally:
    GPIO.cleanup()
