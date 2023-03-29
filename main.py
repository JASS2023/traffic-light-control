import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt
import os

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
client.loop_forever()

if "FALSE" == os.environ['TRAFFIC_LIGHT_IS_LEADER']:
    try:
        def on_connect(client, userdata, flags, rc, properties=None):
            client.subscribe("topic/lights")
        def on_message(client, userdata, msg):
            GPIO.cleanup()
            if msg.payload.decode() == "red":
                # Red phase
                GPIO.output(LED_RED_GPIO, GPIO.HIGH)
            if msg.payload.decode() == "yellow":
                # Yellow phase
                GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
            if msg.payload.decode() == "green":
                # Green phase
                GPIO.output(LED_GREEN_GPIO, GPIO.HIGH)
            if msg.payload.decode() == "prepare":
                # pre green 
                GPIO.output(LED_RED_GPIO, GPIO.HIGH)
                GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
        client.on_connect = on_connect
        client.on_message = on_message
    except KeyboardInterrupt:
      pass
else:
  try:
    while True:
        # Red phase => Other green
        client.publish("topic/lights", "green")
        GPIO.cleanup()
        GPIO.output(LED_RED_GPIO, GPIO.HIGH)
        sleep(5)
                
        # Prepare green => Other yellow
        client.publish("topic/lights", "yellow")
        GPIO.cleanup()
        GPIO.output(LED_RED_GPIO, GPIO.HIGH)
        GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
        
        # Green phase => Other red
        client.publish("topic/lights", "red")
        GPIO.cleanup()
        GPIO.output(LED_GREEN_GPIO, GPIO.HIGH)
        
        # Yellow phase => Other prepare 
        client.publish("topic/lights", "prepare")
        GPIO.cleanup()
        GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
  except KeyboardInterrupt:
    pass
  finally:
    GPIO.cleanup()
