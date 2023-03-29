import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt

#It's a subscriber

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

def on_connect(client,userdata,rc):
    client.subscribe("topic/lights")

def on_message(client,userdata,msg):
    if msg.payload.decode() == "red":
        turn_on_led(LED_RED_GPIO)
    if msg.payload.decode() == "yellow":
        turn_on_led(LED_YELLOW_GPIO)
    if msg.payload.decode() == "green":
        turn_on_led(LED_GREEN_GPIO)
    client.disconnect();

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.0.213", 1883, 60)

client.loop_forever()

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()    
