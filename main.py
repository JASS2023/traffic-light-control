import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt
import json
import os

LED_RED_GPIO = 14
LED_YELLOW_GPIO = 18
LED_GREEN_GPIO = 24

CLEARANCE_TIME = 5 # TODO: Calculate based on speed/distance
GREEN_TIME = 7
YELLOW_TIME = 2
PREPARE_TIME = 2

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_GREEN_GPIO, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_RED_GPIO, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(LED_YELLOW_GPIO, GPIO.OUT, initial=GPIO.LOW)

client = mqtt.Client()

traffic_light_group = os.environ['TRAFFIC_LIGHT_GROUP']
traffic_light_id = os.environ['TRAFFIC_LIGHT_ID']
traffic_lights_coords = os.environ['ALL_TRAFFIC_COORDS'].split(";")
traffic_lights_x = []
traffic_lights_y = []
traffic_lights_yaw = []
traffic_lights_counter = []
yaw_buffer = {}

for i in range(len(traffic_lights_coords)):
    if i%3 == 0:
        traffic_lights_counter.append(0)
        traffic_lights_x.append(float(traffic_lights_coords[i]))
    elif i%3 == 1:
        traffic_lights_y.append(float(traffic_lights_coords[i]))
    elif i%3 == 2:
        traffic_lights_yaw.append(float(traffic_lights_coords[i]))

topic = f"traffic-light/{traffic_light_group}/{traffic_light_id}"
vehicleStatusTopic = "vehicle/+/status"

def on_connect(client, userdata, flags, rc, properties=None):
    client.subscribe(topic)
    if "FALSE" != os.environ['TRAFFIC_LIGHT_IS_LEADER']:
        client.subscribe(vehicleStatusTopic)
    print("Did subscribe to topic(s)")

def average(lst):
    return sum(lst) / len(lst)

def on_message(client, userdata, msg):
    if msg.topic.find("traffic-light") != -1:
        GPIO.output(LED_RED_GPIO, GPIO.LOW)
        GPIO.output(LED_YELLOW_GPIO, GPIO.LOW)
        GPIO.output(LED_GREEN_GPIO, GPIO.LOW)
        
        decoded_msg_vehicle = msg.payload.decode()
        parsed_msg = json.loads(decoded_msg_vehicle)["data"]
        match parsed_msg["color"]:
            case "red":
                GPIO.output(LED_RED_GPIO, GPIO.HIGH)
            case "yellow":
                GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
            case "green":
                GPIO.output(LED_GREEN_GPIO, GPIO.HIGH)
            case "prepare":
                GPIO.output(LED_RED_GPIO, GPIO.HIGH)
                GPIO.output(LED_YELLOW_GPIO, GPIO.HIGH)
    elif msg.topic.find("vehicle") != -1 & msg.topic.find("status") != -1:
        decoded_msg_vehicle = msg.payload.decode()
        parsed_msg = json.loads(decoded_msg_vehicle)["data"]

        if not parsed_msg["id"] in yaw_buffer:
            yaw_buffer[parsed_msg["id"]] = []
        
        yaw_buffer[parsed_msg["id"]].append(float(parsed_msg["coordinates"]["yaw"]))

        if len(yaw_buffer[parsed_msg["id"]]) > 5:
            yaw_buffer[parsed_msg["id"]].pop(0)

        avg_yaw = average(yaw_buffer[parsed_msg["id"]]) % 360

        valid_tl_ids = []

        for i in range(len(traffic_lights_counter)):
            traffic_light_yaw = traffic_lights_yaw[i]
            if (avg_yaw <= ((traffic_light_yaw + 30) % 360)) & (avg_yaw >= ((traffic_light_yaw - 30) % 360)):
                valid_tl_ids.append(i)

        x = float(parsed_msg["coordinates"]["x"])
        y = float(parsed_msg["coordinates"]["y"])
                
        min_dist = abs(x - traffic_lights_x[0]) + abs(y - traffic_lights_y[0])
        min_i = 0
        for i in valid_tl_ids:
            dist = abs(x - traffic_lights_x[i]) + abs(y - traffic_lights_y[i])
            if min_dist > dist:
                min_i = i
                min_dist = dist
        if min_dist <= 1:
            traffic_lights_counter[min_i] += 1
             
        

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

        json_prefix = "{ \"type\": \"status_traffic-light\", \"data\": { \"color\": \""
        json_suffix = "\" } }"

        for i in traffic_light_ids:
            client.publish(f"traffic-light/{traffic_light_group}/{i}", json_prefix + "red" + json_suffix)
        
        while True:
            max_count = traffic_lights_counter[0]
            max_j = 0
            for j in range(len(traffic_lights_counter)):
                if max_count < traffic_lights_counter[j]:
                    max_count = traffic_lights_counter[j]
                    max_j = j
            if max_count > 0:
                i = max_j
            else:
                sleep(0.5)
                continue
            
            sleep(2) # Artificial sleep for demo
            current_traffic_light = f"traffic-light/{traffic_light_group}/{traffic_light_ids[i]}"
            
            client.publish(current_traffic_light, json_prefix + "prepare" + json_suffix)
            sleep(PREPARE_TIME)
            client.publish(current_traffic_light, json_prefix + "green" + json_suffix)
            traffic_lights_counter[i] = 0
            sleep(GREEN_TIME)
            client.publish(current_traffic_light, json_prefix + "yellow" + json_suffix)
            sleep(YELLOW_TIME)
            client.publish(current_traffic_light, json_prefix + "red" + json_suffix)
            sleep(CLEARANCE_TIME)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
