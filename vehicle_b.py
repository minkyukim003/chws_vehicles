import paho.mqtt.client as mqtt
import time, json, cv2, os
from ultralytics import YOLO

FRAME_INTERVAL = 0.1
KITTI_PATH = "./KITTI/testing/image_2"
DUMMY_PATH = "./dummy.png"

EDGE_IP = "ENTER YOUR IP HERE"

model = YOLO("yolov8n.pt")


# Trial state
trial_active = False
hazard_idx = None
B_start = None

start_time = None
received_chws = False
t_chws = None

running = True
last_payload = None


def compute_travel_time():
    """Local travel time until hazard frame."""
    return (hazard_idx - B_start) * FRAME_INTERVAL

def safe_json_decode(msg):
    try:
        return json.loads(msg.payload.decode())
    except Exception:
        print("[B] Ignoring non-JSON message:", msg.payload)
        return None


def on_message(client, userdata, msg):
    global trial_active, hazard_idx, B_start
    global start_time, received_chws, t_chws
    global last_payload, running

    # ---------------------------
    # Warm-up pong
    # ---------------------------
    if topic == "warmup/pong":
        print("[B] Pong received.")
        return

    payload = safe_json_decode(msg)
    if payload is None:
        return

    topic = msg.topic

    # ---------------------------
    # Trial Start
    # ---------------------------
    if topic == "vehicleB/start" and trial_active == False:

        last_payload = payload
        hazard_idx = payload["hazard_idx"]
        B_start = payload["B_start"]

        start_time = time.time()
        trial_active = True
        received_chws = False
        t_chws = None

        print(f"\n[B] Trial {payload['trial']} started (Scenario {payload['scenario']})")
        print(f"[B] hazard_idx={hazard_idx}, B_start={B_start}")

    # ---------------------------
    # CHWS arrives
    # ---------------------------
    elif topic == "vehicleB/hazard" and trial_active and not received_chws:
        t_chws = time.time() - start_time
        received_chws = True
        print(f"[B] CHWS received at t={t_chws:.3f}s")

    # ---------------------------
    # Shutdown
    # ---------------------------
    elif topic == "experiment/end":
        print("[B] Shutdown signal received.")
        running = False


def perform_local_detection():
    """YOLO detection on the hazard frame."""
    image_name = f"{hazard_idx:06d}.png"
    image_path = os.path.join(KITTI_PATH, image_name)
    img = cv2.imread(image_path)

    if img is None:
        print("[B] ERROR: Could not load image:", image_path)
        return None

    start_det = time.time()
    result = model(img, verbose=False)[0]
    det_time = time.time() - start_det

    valid = ["person","bicycle","car","motorcycle","bus","truck","train"]
    for box in result.boxes:
        if model.names[int(box.cls)] in valid:
            return det_time

    return None



def main():

    global trial_active

    model.predict(DUMMY_PATH, verbose=False)
    print("[B] YOLO model loaded and warmed up.")

    client = mqtt.Client("VehicleB")
    client.connect(EDGE_IP, 1883, keepalive=300)

    client.subscribe("vehicleB/start")
    client.subscribe("vehicleB/hazard")
    client.subscribe("experiment/end")

    client.subscribe("warmup/pong")

    client.on_message = on_message
    client.loop_start()

    with open("vehicle_b_results.csv", "w") as f:
        f.write("trial,scenario,travel_time,local_yolo_time,t_local_total,t_chws,final_time,improvement\n")

    print("[B] Ready for trials...")

    counter = 0
    while running:
        time.sleep(0.05)

        if trial_active:

            travel_time = compute_travel_time()

            time.sleep(2)

            local_yolo_time = perform_local_detection()
            if local_yolo_time is not None:
                print(f"[B] Local YOLO detect = {local_yolo_time:.3f}s (travel={travel_time:.3f}s)")
            else:
                print("[B] WARNING: No hazard found by YOLO.")
                local_yolo_time = 0

            t_local_total = travel_time + local_yolo_time

            # Determine final detection time
            if received_chws:
                final_time = min(t_local_total, t_chws)
            else:
                final_time = t_local_total

            improvement = t_local_total - final_time

            # Save results
            # "travel_time" refers to the travel time of B!
            
            if counter != 0:
                with open("vehicle_b_results.csv", "a") as f:
                    f.write(
                        f"{last_payload['trial']},{last_payload['scenario']},"
                        f"{travel_time:.3f},{local_yolo_time:.3f},{t_local_total:.3f},"
                        f"{t_chws if t_chws else 0:.3f},{final_time:.3f},{improvement:.3f}\n"
                    )
                
            elif counter == 0:
                print("[B] Skipping dummy trial result logging.")

            print(f"[B] Final time = {final_time:.3f}s (Improvement {improvement:.3f}s)\n")

            trial_active = False
            counter += 1

    client.loop_stop()
    client.disconnect()
    exit()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n[B] Exiting...")
