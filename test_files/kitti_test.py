import os, cv2

KITTI_TRAINING_PATH = "./KITTI/training/image_2"

images = sorted(os.listdir(KITTI_TRAINING_PATH))

print(f"Number of images: {len(images)}.")
print(f"First five frames: {images[:5]}")

image = cv2.imread(os.path.join(KITTI_TRAINING_PATH,images[0]))
print(f"Size of image 0: {image.shape}.")