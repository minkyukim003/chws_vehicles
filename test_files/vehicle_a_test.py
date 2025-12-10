#th121-2

import paho.mqtt.client as mqtt
import json, time

EDGE_IP = "100.103.240.89"

client = mqtt.Client("VehicleA")
client.connect(EDGE_IP, 1883)

print("[Vehicle A] Connected. Sending hazards…")

try:
    while True:
        #This part is replaced with real data.
        hazard = {
            "vehicle_id": "A",
            "hazard_type": "pedestrian",
            "location": [10, 20],
            "timestamp": time.time()
        }

        client.publish("vehicle/A/hazard", json.dumps(hazard))
        print("[Vehicle A] Sent:", hazard)
        time.sleep(3)

except KeyboardInterrupt:
    print("Disconnected vehicle A. Not sending hazard.")

#Send hazard to edge