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

traffic_light_group = os.environ['TRAFFIC_LIGHT_GROUP']
traffic_light_id = os.environ['TRAFFIC_LIGHT_ID']

topic = f"traffic-light/{traffic_light_group}/{traffic_light_id}"

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

client.on_connect = on_connect
client.on_message = on_message

print("Connecting...")
client.connect(os.environ['MQTT_BROKER_IP'], int(os.environ['MQTT_BROKER_PORT']))
print("Connected")

try: 
    if "FALSE" == os.environ['TRAFFIC_LIGHT_IS_LEADER']:
        print("I am NOT the LEADER")
        
        client.loop_forever()
    else:
        print("I am the LEADER")
        
        client.loop_start()
        
        traffic_light_ids = os.environ['ALL_TRAFFIC_LIGHT_IDS'].split(",")

        for i in traffic_light_ids:
            client.publish(f"traffic-light/{traffic_light_group}/{i}", "red")
        
        i = 0
        
        while True:
            i += 1
            i = i % len(traffic_light_ids)
            
            current_traffic_light = f"traffic-light/{traffic_light_group}/{traffic_light_ids[i]}"
            
            sleep(CLEARANCE_TIME)
            client.publish(current_traffic_light, "prepare")
            sleep(PREPARE_TIME)
            client.publish(current_traffic_light, "green")
            sleep(GREEN_TIME)
            client.publish(current_traffic_light, "yellow")
            sleep(YELLOW_TIME)
            client.publish(current_traffic_light, "red")
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
