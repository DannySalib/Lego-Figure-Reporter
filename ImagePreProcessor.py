from PIL import Image
from enum import Enum

# download quality types for future changes 
class IMAGE_DOWNLOAD_QUALITY(Enum):
    LOW = 85
    HIGH = 95

class IMAGE_RESOLUTION_QUALITY(Enum):
    LOW = (64, 64)
    HIGH = (96, 96)

class ImagePreprocessor:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def format(image: Image.Image):
        return image.resize(IMAGE_RESOLUTION_QUALITY.HIGH.value, Image.Resampling.LANCZOS)
    
    @staticmethod
    def save_to(image: Image.Image, path: str):
        image.save(path, 'JPEG', quality=IMAGE_DOWNLOAD_QUALITY.LOW.value, optimize=True)
