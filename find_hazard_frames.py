import os
import cv2
import random
from ultralytics import YOLO

"""
CITATION:
Ultralytics YOLOv8, version 8.0.0
Glenn Jocher, Ayush Chaurasia, Jing Qiu (2023)
https://github.com/ultralytics/ultralytics
"""

# Path to KITTI test images
KITTI_PATH = "./KITTI/testing/image_2"

# YOLO hazard classes
HAZARD_CLASSES = [
    "person", "bicycle", "car", "motorcycle",
    "bus", "truck", "train"
]

OUTPUT_FILE = "hazard_idx.txt"


def main():
    # Load YOLO
    model = YOLO("yolov8n.pt")
    model.to("cuda")

    # Load image list (sorted ensures correct frame indexing)
    images = [img for img in os.listdir(KITTI_PATH) if img.endswith(".png")]
    hazard_indices = []

    print("Starting YOLO scan of KITTI test set...\n")

    counter = 0
    # Loop over all frames
    for filename in images:
        if counter == 101:
            break

        img_path = os.path.join(KITTI_PATH, filename)
        img = cv2.imread(img_path)

        results = model(img, verbose=False)[0]

        # Check if frame contains a hazard class
        contains_hazard = False
        for box in results.boxes:
            class_name = model.names[int(box.cls)]
            if class_name in HAZARD_CLASSES:
                contains_hazard = True
                break

        idx = int(filename.split(".")[0])  # Frame index from filename

        if contains_hazard:
            print(f"[FOUND HAZARD] Frame {idx} ({filename})")
            hazard_indices.append(idx)

        counter += 1 

    if not hazard_indices:
        print("\nERROR: no hazards found in dataset!")
        return

    # Randomize order for experiment
    random.shuffle(hazard_indices)

    # Save file
    with open(OUTPUT_FILE, "w") as f:
        for idx in hazard_indices:
            f.write(str(idx) + "\n")

    print(f"\nSaved {len(hazard_indices)} hazard indices to {OUTPUT_FILE}")
    print(f"Example output:", hazard_indices[:10])


if __name__ == "__main__":
    main()
