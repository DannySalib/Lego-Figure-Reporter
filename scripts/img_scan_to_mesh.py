import os 
from dotenv import load_dotenv
import cv2
import re 
import hashlib
import time 
from datetime import datetime
from PIL import Image
import subprocess

from ImagePreProcessor import ImagePreprocessor

load_dotenv()

# file structure styled db?
ROOT: str = "./scans"
os.makedirs(ROOT, exist_ok=True)

IP_REGEX: str = (
    r"^(?:25[0-5]|2[0-4][0-9]|?[0-9][0-9]?)\\."
      r"(?:25[0-5]|2[0-4][0-9]|?[0-9][0-9]?)\\."
       r"(?:25[0-5]|2[0-4][0-9]|?[0-9][0-9]?)\\."
        r"(?:25[0-5]|2[0-4][0-9]|?[0-9][0-9]?)$"
)

""" 
TODO 
replace sleep by lowering FPS instead 

dont use hash and just use datetime str fmt 

use an xbox 360 kinect as camera/lidar?

use COLMAP to convert images into a mesh 

after converting to mesh, replace images with lower quality to save space?
    - delete images?

"""
def main():
    print("Please have DroidCam installed and steup on phone!")
    ip: str = os.environ.get("CIP") or ask_for_ip()
        
    # using droid cam
    url: str = f"http://{ip}:4747/videofeed"
    cap: cv2.VideoCapture = cv2.VideoCapture(url)

    if not cap.isOpened():
        raise ValueError("Could not open video device")

    # create a path to our imgs for this scan
    scan_id: str = hashlib.sha256(str(datetime.now()).encode('utf-8')).hexdigest()
    try:
        os.makedirs(f'{ROOT}/{scan_id}')
    except OSError as e:
        raise OSError(f"A collision in file system has occured. {scan_id = }") from e

    os.makedirs(f'{ROOT}/{scan_id}/imgs', exist_ok=True)

    print("Hit enter to start collecting images and press `q` to end collection...")
    input()

    img_idx: int = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.imshow('Cam', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # sve into filesystem with some processing first 
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        ImagePreprocessor.format(img)
        ImagePreprocessor.save_to(img, f'{ROOT}/{scan_id}/imgs/{img_idx}.jpg')
        
        img_idx += 1
        time.sleep(1)
    
    

    cap.release()
    cv2.destroyAllWindows()

def ask_for_ip() -> str:
    while True:
        ip = input("Please provide an IP for camera access")
        if re.match(IP_REGEX, ip):
            return ip
        else:
            print("Invalid IP. Please try again.")

if __name__ == '__main__':
    main()