import paho.mqtt.client as mqtt

EDGE_IP = "YOUR EDGE IP HERE"  # <-- replace this with your laptop WiFi IP

client = mqtt.Client("SchoolTest")

try:
    client.connect(EDGE_IP, 1883, 60)
    print("Successfully connected to the laptop MQTT broker!")
except Exception as e:
    print("Connection failed:", e)
