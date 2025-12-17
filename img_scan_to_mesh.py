from enum import Enum
import os 
from dotenv import load_dotenv
import cv2
import re 
import hashlib
import time 
from datetime import datetime
from PIL import Image
import subprocess
from pathlib import Path
from itertools import count

from ImagePreProcessor import ImagePreprocessor

load_dotenv()

# file structure styled db?
WORKSPACE: Path = Path(__file__).parent / "scans"

IP_REGEX: str = (
    r"^(?:25[0-5]|2[0-4][0-9]|?[0-9][0-9]?)\\."
      r"(?:25[0-5]|2[0-4][0-9]|?[0-9][0-9]?)\\."
       r"(?:25[0-5]|2[0-4][0-9]|?[0-9][0-9]?)\\."
        r"(?:25[0-5]|2[0-4][0-9]|?[0-9][0-9]?)$"
)

MAX_COLLECTION: int = 200

""" 
TODO 
use an xbox 360 kinect as camera/lidar?

use COLMAP to convert images into a mesh 

after converting to mesh, replace images with lower quality to save space?
    - delete images?

"""

class ImgCollection:
    ID_FMT: str = "%Y_%m_%d_%H_%M_%S"
    IMG_DIR_NAME: str = "images"

    def __init__(self, workspace: Path):
        os.makedirs(workspace, exist_ok=True)
        self._workspace: Path = workspace
        self._id: str = datetime.now().strftime(ImgCollection.ID_FMT)
        self._collection_path: Path = self._workspace / self._id / ImgCollection.IMG_DIR_NAME
        self._idx_img: count = count(0)

    def get_collection_path(self) -> Path:
        # creates a file structure for img collecting
        # workspace
        # | id
        # | | imgs <- collection path 

        if not os.path.exists(self._collection_path):
            # TODO collision errors?
            os.makedirs(self._collection_path, exist_ok=True)
        
        return self._collection_path

    def collect_frame(self, frame: cv2.typing.MatLike) -> None:
        frame_rgb: cv2.typing.MatLike = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img: Image = Image.fromarray(frame_rgb)
        # instead of using an idx i just hash the datetime
        img_path = self.get_collection_path() / f"{next(self._idx_img)}.jpg"
        ImagePreprocessor.save_to(img, img_path)

class CaptureMethod(Enum):
    CAMERA: int = 0
    
class VideoCaptureDevice:
    FPS: int = 25

    def __init__(self, method: CaptureMethod):
        
        filename: str
        match method:
            case CaptureMethod.CAMERA:
                ip = os.environ.get("CIP") or self._ask_for_ip()
                filename = f"http://{ip}:4747/videofeed"
            case _:
                raise NotImplementedError()
        
        self._cap: cv2.VideoCapture = cv2.VideoCapture(filename)
        self._cap.set(cv2.CAP_PROP_FPS, VideoCaptureDevice.FPS) 
        if not self._cap.isOpened():
            raise ValueError("Could not open video device")
    
    def read(self) -> tuple[bool, cv2.typing.MatLike]:
        return self._cap.read()
    
        
    def _ask_for_ip(self) -> str:
        while True:
            ip = input("Please provide an IP for camera access: ")
            if re.match(IP_REGEX, ip):
                return ip
            else:
                print("Invalid IP. Please try again.")   

def main():
    print("Please have DroidCam installed and steup on phone if u plan on using it!")
    cap = VideoCaptureDevice(CaptureMethod.CAMERA)

    print("Hit enter to start collecting images and press `CTRL+C` to end collection...")
    input()

    collector: ImgCollection = ImgCollection(WORKSPACE)
    print("COLLECTING...")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow('Cam', frame)
            collector.collect_frame(frame)
    except KeyboardInterrupt:
        pass # TODO figure out how to quit properly 
    finally:
        cap._cap.release()
        cv2.destroyAllWindows()
        print("DONE!")

    remove_excess_captures(
        collection_path=collector.get_collection_path(),
        max_collection=MAX_COLLECTION
    ) 

    print(f"Ended with {len(os.listdir(collector.get_collection_path()))} photos")

    print("Getting mesh...")
    visualize(
        fused_path=colmapper(collector.get_collection_path())
    )


def remove_excess_captures(collection_path: Path, max_collection: int) -> None:
    if not os.path.exists(collection_path):
        raise ValueError(f"{collection_path} does not exist")

    collection: list[str] = os.listdir(collection_path)
    if len(collection) <= max_collection:
        return
    
    # evenly remove excess photos throughout collection 
    step: int = (len(collection)-1) / (max_collection-1)
    idx_keep: set[int] = {
        round(i * step)
        for i in range(len(collection))
    }

    for i, c in enumerate(collection):
        if i not in idx_keep:
            os.remove(collection_path / c)

def colmapper(colection_path: Path) -> Path:
    root: Path = colection_path.parent
    db_path: Path = root / "datbase.db"
    sparse_path: Path = root / "sparse"
    os.makedirs(sparse_path, exist_ok=True)
    dense_path: Path = root / "dense"
    os.makedirs(dense_path, exist_ok=True)
    
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", db_path,
        "--image_path", colection_path,
        "--ImageReader.single_camera", "1",
        "--SiftExtraction.max_num_features", "8192"
    ])

    subprocess.run([
        "colmap", "sequential_matcher",
        "--database_path", db_path,
        "--SequentialMatching.overlap", "10",
    ])
    
    subprocess.run([
        "colmap", "mapper",
        "--database_path", db_path,
        "--image_path", colection_path,
        "--output_path", sparse_path,
        "--Mapper.min_num_matches", "20"
    ])

    if not os.listdir(sparse_path):
        raise IOError("Error with colmap mapper")

    subprocess.run([
        "colmap", "image_undistorter",
        "--image_path", colection_path,
        "--input_path", sparse_path/"0",
        "--output_path", dense_path,
        "--output_type", "COLMAP"
    ])

    if not os.listdir(dense_path):
        raise IOError("Error with colmap image undistorter")

    subprocess.run([
        "colmap", "patch_match_stereo",
        "--workspace_path", dense_path,
        "--workspace_format", "COLMAP",
        "--PatchMatchStereo.geom_consistency", "true",
    ])

    subprocess.run([
        "colmap", "stereo_fusion",
        "--workspace_path", dense_path,
        "--workspace_format", "COLMAP",
        "--input_type", "geometric",
        "--output_path", dense_path/"fused.ply"
    ])

    if os.path.exists(dense_path/"fused.ply"):
        return  dense_path/"fused.ply"
    else:
        raise IOError("Could not make mesh with colmap pipeline")
    
def visualize(fused_path: Path) -> None:
    subprocess.run([
        "meshlab", fused_path
    ])

if __name__ == '__main__':
    main()
        