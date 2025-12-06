import cv2
import os
import yaml

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)


def extract_images(video_path):
    """Extract frames from video at configured rate."""
    RATE = CONFIG["rate"]
    
    vid = cv2.VideoCapture(video_path)
    if not os.path.exists("images"):
        os.makedirs("images")
    
    count, success = 0, True
    frame_count = 0
    while success:
        success, image = vid.read()
        if success and count % RATE == 0:
            cv2.imwrite(f"./images/frame{count // RATE}.jpg", image)
            frame_count += 1
        count += 1
    
    vid.release()
    print(f"Extracted {frame_count} frames from video")
    return frame_count


if __name__ == "__main__":
    extract_images("videos/WhatsApp Video 2025-12-01 at 17.27.58.mp4")
