import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt
import os

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

client = mqtt.Client()
client.connect(os.environ['MQTT_BROKER_IP'], int(os.environ['MQTT_BROKER_PORT']))

if "FALSE" == os.environ['TRAFFIC_LIGHT_IS_LEADER']:
    try:
        def on_connect(client, userdata, flags, rc, properties=None):
            client.subscribe("topic/lights")
        def on_message(client, userdata, msg):
            if msg.payload.decode() == "red":
                # Red phase
                turn_on_led(LED_RED_GPIO, duration=14)
            if msg.payload.decode() == "yellow":
                # Yellow phase
                turn_on_led(LED_YELLOW_GPIO, duration=2)
            if msg.payload.decode() == "green":
                # Green phase
                turn_on_led(LED_GREEN_GPIO, duration=10)
            if msg.payload.decode() == "prepare":
                # Prepare green 
                turn_on_led(LED_RED_GPIO, LED_YELLOW_GPIO, duration=2)
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_forever()
        client.disconnect();
    except KeyboardInterrupt:
      pass
else:
  try:
    while True:
        # Red phase
        turn_on_led(LED_RED_GPIO, duration=14)
        # Another traffic works
        client.publish("topic/lights", "prepare")
        client.publish("topic/lights", "green")
        client.publish("topic/lights", "yellow")
        client.publish("topic/lights", "red")
        # Prepare green
        turn_on_led(LED_RED_GPIO, LED_YELLOW_GPIO, duration=2)
        # Yellow phase
        turn_on_led(LED_YELLOW_GPIO, duration=2)
        # Green phase
        turn_on_led(LED_GREEN_GPIO, duration=10)
        client.disconnect();
  except KeyboardInterrupt:
    print("Stopped")
    pass
  finally:
    GPIO.cleanup()
