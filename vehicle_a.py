# vehicle_a.py -----------------------------------------------------
import paho.mqtt.client as mqtt
import time, json, os, cv2
from ultralytics import YOLO

EDGE_IP = "100.103.240.89"
FRAME_INTERVAL = 0.1
KITTI_PATH = "/home/mkim24/home/graduate/csci680/chws/KITTI/testing/image_2"

ack_received = None

# Load YOLO model once
model = YOLO("yolov8n.pt")
model.to("cuda")

def load_hazard_indices(path="./hazard_idx.txt"):
    with open(path, "r") as f:
        return [int(x.strip()) for x in f.readlines()]

def scenario_params(scenario, hazard_idx):
    # Only modifying B_start.
    if scenario == 1:
        return hazard_idx, hazard_idx - 50
    if scenario == 2:
        return hazard_idx, hazard_idx - 30
    if scenario == 3:
        return hazard_idx, hazard_idx - 20
    if scenario == 4:
        return hazard_idx, hazard_idx - 10
    if scenario == 5:
        return hazard_idx, hazard_idx

def perform_yolo_detection(hazard_idx):
    """Runs YOLO on the hazard frame and returns detection time."""
    img_name = f"{hazard_idx:06d}.png"
    img_path = os.path.join(KITTI_PATH, img_name)

    img = cv2.imread(img_path)
    if img is None:
        print(f"[A] ERROR: Could not load image {img_path}")
        return None

    start = time.time()
    result = model(img, verbose=False)[0]
    det_time = time.time() - start

    valid_classes = [
        "person", "bicycle", "car", "motorcycle",
        "bus", "truck", "train"
    ]

    for box in result.boxes:
        if model.names[int(box.cls)] in valid_classes:
            return det_time

    return None  # YOLO failed to detect anything meaningful


def run_trial(trial, scenario, hazard_idx, client):

    A_start, B_start = scenario_params(scenario, hazard_idx)
    A_start = max(A_start, 0)
    B_start = max(B_start, 0)

    print(f"\n=== Trial {trial} | Scenario {scenario} ===")
    print(f"A_start={A_start}, B_start={B_start}, hazard_idx={hazard_idx}")

    # Inform Vehicle B of the trial setup
    client.publish("experiment/start", json.dumps({
        "trial": trial,
        "scenario": scenario,
        "hazard_idx": hazard_idx,
        "A_start": A_start,
        "B_start": B_start
    }))

    time.sleep(0.2)

    # ----------------------------
    # Simulate travel time
    # ----------------------------
    travel_frames = hazard_idx - A_start
    travel_time = travel_frames * FRAME_INTERVAL

    # ----------------------------
    # YOLO detection at hazard
    # ----------------------------
    det_time = perform_yolo_detection(hazard_idx)

    if det_time is None:
        print(f"[A] WARNING: YOLO detected NO hazard at frame {hazard_idx}.")
        det_time = 0.0  # Use zero so CHWS still sends

    # ----------------------------
    # Send CHWS message
    # ----------------------------
    hazard_msg = {
        "vehicle": "A",
        "hazard_idx": hazard_idx,
        "timestamp": time.time(),
        "yolo_detection_time": det_time,
        "travel_time": travel_time,
        "total_A_time": travel_time + det_time
    }

    client.publish("hazard/chws", json.dumps(hazard_msg))

    print(f"[A] CHWS sent for hazard_idx={hazard_idx} "
          f"(detect={det_time:.3f}s, travel={travel_time:.3f}s)")

    # Small delay before next trial
    time.sleep(0.5)


def main():
    client = mqtt.Client("VehicleA")
    client.connect(EDGE_IP, 1883, keepalive=300)

    client.loop_start()

    hazard_list = load_hazard_indices("./hazard_idx.txt")
    scenario_list = [1, 2, 3, 4, 5]

    for _ in range(5):
        client.publish("warmup/ping", "ping")
        print("[A] Sent warmup ping.")
        time.sleep(0.2)
    print("[A] Warmed up connection.")

    # Dummy trial
    print("\n[A] Starting dummy trial for warm-up...")
    dummy_hazard = hazard_list[0]
    run_trial(0, scenario_list[0], dummy_hazard, client)
    time.sleep(2)

    print("\n[A] Starting real trials...")
    # Real trials
    for trial, hazard_idx in enumerate(hazard_list, start=1):
        scenario = scenario_list[(trial - 1) % 5]
        run_trial(trial, scenario, hazard_idx, client)
        time.sleep(3)

    # Tell B to shut down
    client.publish("experiment/end", json.dumps({"status":"done"}))
    time.sleep(0.3)

    client.loop_stop()
    client.disconnect()
    print("[A] Finished all trials and shut down.")


if __name__ == "__main__":
    try:
        main()
    
    except KeyboardInterrupt:
        print("\n[A] Exiting...")
