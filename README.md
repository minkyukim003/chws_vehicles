# CHWS Vehicles
This repository contains the files that simulates the vehicles in my CHWS system. 

## Files in this repo. 
    /test_files
        /kitti_test.py
        /mqtt_test.py
        /vehicle_a_test.py
        /vehicle_b_test.py
    /dummy.png
    /find_hazard_frames.py
    /vehicle_a.py
    /vehicle_b.py
    /vehicle_c.py

### Required installation for connection
    mosquitto

### Required imports for Python
    Ultralytics YOLO
    paho

### Other installations
    You must have the KITTI dataset in your working folder.

kitti_test.py
    This file tests if the YOLO model works on the KITTI dataset. 
mqtt_test.py
    Tests connection with edge device.
vehicle_a_test.py
    Tests if vehicle A works as expected when working with vehicle_b_test.py and the edge server test.
vehicle_b_test.py
    Same as above but for vehicle B.
dummy.png
    This is used by the YOLO model to warm up. 
find_hazard_frames.py
    This file finds 100 frames in the KITTI dataset that contain hazards and shuffles them, outputting hazard_idx.txt, which includes the randomly selected and shuffled hazard indices. 
vehicle_a.py 
    This file simulates CHWS vehicle A by sending hazard information to B through edge.
vehicle_b.py 
    This file simulates CHWS vehicle B by receiving information from A through edge. It also performs local YOLO detections. This file outputs vehicle_b_results.csv. 
vehicle_c.py 
    This file simulates local vehicle C by performing local YOLO detections. This file outputs vehicle_c_results.csv. 

The CHWS connections must established by following the procedure below.
1. Start a mosquitto process on your edge device.
2. Start your Python edge server. Wait for connection establishment. 
3. Start vehicle_b.py. Wait for connection establishment. 
4. Start vehicle_a.py. 
