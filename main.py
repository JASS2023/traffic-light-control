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

if "FALSE" == os.environ['TRAFFIC_LIGHT_IS_LEADER']:
    print("I am NOT the LEADER")
    try:
        def on_connect(client, userdata, flags, rc, properties=None):
            client.subscribe("topic/lights")
            print("Did subscribe to topic")
        def on_message(client, userdata, msg):
            print("Got a message: " + msg.payload.decode())
            GPIO.output(LED_RED_GPIO, GPIO.LOW)
            GPIO.output(LED_YELLOW_GPIO, GPIO.LOW)
            GPIO.output(LED_GREEN_GPIO, GPIO.LOW)
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
        print("Connecting...")
        client.connect(os.environ['MQTT_BROKER_IP'], int(os.environ['MQTT_BROKER_PORT']))
        print("Connected")
        client.loop_forever()
    except KeyboardInterrupt:
      pass
else:
  print("I am the LEADER")
  try:
    print("Connecting...")
    client.connect(os.environ['MQTT_BROKER_IP'], int(os.environ['MQTT_BROKER_PORT']))
    client.publish("topic/lights", "red")
    print("Connected")
    while True:
        GPIO.output(LED_YELLOW_GPIO, GPIO.LOW)
        GPIO.output(LED_RED_GPIO, GPIO.HIGH)
        sleep(2) # clearance phase
        client.publish("topic/lights", "prepare")
        sleep(2) # prepare non-leader
        client.publish("topic/lights", "green")
        sleep(5) # green non-leader
                
        client.publish("topic/lights", "yellow")
        sleep(2) # yellow non-leader
        client.publish("topic/lights", "red")
        sleep(2) # clearance phase
        GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
        sleep(2) # prepare leader
        
        GPIO.output(LED_RED_GPIO, GPIO.LOW)
        GPIO.output(LED_YELLOW_GPIO, GPIO.LOW)
        GPIO.output(LED_GREEN_GPIO, GPIO.HIGH)
        sleep(5) # green leader
        
        GPIO.output(LED_GREEN_GPIO, GPIO.LOW)
        GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
        sleep(2) # yellow leader
  except KeyboardInterrupt:
    pass
  finally:
    GPIO.cleanup()
