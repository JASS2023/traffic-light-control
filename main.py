import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt
import os

LED_RED_GPIO = 14
LED_YELLOW_GPIO = 18
LED_GREEN_GPIO = 24

CLEARANCE_TIME = 3 # TODO: Calculate based on speed/distance
GREEN_TIME = 5
YELLOW_TIME = 2
PREPARE_TIME = 2

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_GREEN_GPIO, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_RED_GPIO, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_YELLOW_GPIO, GPIO.OUT, initial=GPIO.LOW)

client = mqtt.Client()
print("Connecting...")
client.connect(os.environ['MQTT_BROKER_IP'], int(os.environ['MQTT_BROKER_PORT']))
print("Connected")
traffic_light_id = os.environ['TRAFFIC_LIGHT_ID']
traffic_light_group = os.environ['TRAFFIC_LIGHT_GROUP']

topic = f"topic/{traffic_light_group}/lights"

def on_connect(client, userdata, flags, rc, properties=None):
    client.subscribe(topic)
    print("Did subscribe to topic")

def on_message(client, userdata, msg):
    print("Got a message: " + msg.payload.decode())
    GPIO.output(LED_RED_GPIO, GPIO.LOW)
    GPIO.output(LED_YELLOW_GPIO, GPIO.LOW)
    GPIO.output(LED_GREEN_GPIO, GPIO.LOW)
    match msg.payload.decode():
        case "red":
            GPIO.output(LED_RED_GPIO, GPIO.HIGH)
        case "yellow":
            GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
        case "green":
            GPIO.output(LED_GREEN_GPIO, GPIO.HIGH)
        case "prepare":
            GPIO.output(LED_RED_GPIO, GPIO.HIGH)
            GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)

try: 
    if "FALSE" == os.environ['TRAFFIC_LIGHT_IS_LEADER']:
        print("I am NOT the LEADER")
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_forever()
    else:
        print("I am the LEADER")
        client.publish(topic, "red")
        while True:
            GPIO.output(LED_YELLOW_GPIO, GPIO.LOW)
            GPIO.output(LED_RED_GPIO, GPIO.HIGH)
            sleep(CLEARANCE_TIME) # clearance phase
            
            client.publish(topic, "prepare")
            sleep(PREPARE_TIME) # prepare non-leader
            
            client.publish(topic, "green")
            sleep(GREEN_TIME) # green non-leader
                    
            client.publish(topic, "yellow")
            sleep(YELLOW_TIME) # yellow non-leader
            
            client.publish(topic, "red")
            sleep(CLEARANCE_TIME) # clearance phase
            
            GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
            sleep(PREPARE_TIME) # prepare leader
            
            GPIO.output(LED_RED_GPIO, GPIO.LOW)
            GPIO.output(LED_YELLOW_GPIO, GPIO.LOW)
            GPIO.output(LED_GREEN_GPIO, GPIO.HIGH)
            sleep(GREEN_TIME) # green leader
            
            GPIO.output(LED_GREEN_GPIO, GPIO.LOW)
            GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
            sleep(YELLOW_TIME) # yellow leader
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
