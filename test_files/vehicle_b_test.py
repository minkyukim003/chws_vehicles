#th121-3

import paho.mqtt.client as mqtt

EDGE_IP = "YOUR EDGE IP HERE"

def on_message(client, userdata, msg):
    print("[Vehicle B] Received hazard:", msg.payload.decode())

client = mqtt.Client("VehicleB")
client.connect(EDGE_IP, 1883)
client.subscribe("hazard/global")
client.on_message = on_message

print("[Vehicle B] Listening…")

try:
    client.loop_forever()

except KeyboardInterrupt:
    print("Disconnected vehicle B. Not receiving hazard information.")

#Receive hazard