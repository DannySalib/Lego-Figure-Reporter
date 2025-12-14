import pandas as pd 
import requests
import os
from zipfile import ZipFile
from io import BytesIO
import logging
from logging import info as print # LMAO 
import logging
from PIL import Image 
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm 

from ImagePreProcessor import ImagePreprocessor
PREFIX: str = ">>"
# setup prefix >> for pretty STDOUT (i overode print) (its my project)
logging.basicConfig(format=f'{PREFIX} %(message)s', level=logging.INFO)

# url to rebrickable's minifig csv 
URL: str = "https://cdn.rebrickable.com/media/downloads/minifigs.csv.zip?1765350724.8110726"
CSV_PATH: str = "./minifigs.csv"
MINIFIG_DATA_PATH: str = "./minifigs"

# an optimization to consider
# what if we already have some figures downloaded? 
# we shouldnt redownload it that's a waste of time 
downloaded: set[str] = set() 

def main() -> None:
    # look for minifigs.csv in current directory 
    # if we havent found one, unzip it from online
    if not os.path.exists(CSV_PATH):
        print(f"Could not find `{CSV_PATH}`. Installing from online...")
        response: requests.Response = requests.get(URL)

        if response.status_code != 200:
            print(f'>> Could not install from online: {response}')
            exit()
        
        with ZipFile(BytesIO(response.content)) as zip_file:
            zip_file.extractall()  # Extracts to the current directory
            print("Files extracted successfully")

    # maybe we didnt successfully unzip?
    if not os.path.exists(CSV_PATH):
        print(f"Something went wrong when getting {CSV_PATH}")
        exit()
    else:
        print(f"Downloading imgs to `{MINIFIG_DATA_PATH}`...")

    # download images into our directory 
    os.makedirs(MINIFIG_DATA_PATH, exist_ok=True)

    global downloaded
    downloaded = set(os.listdir(MINIFIG_DATA_PATH))

    data: np.ndarray = pd.read_csv(
        CSV_PATH,
        usecols = [
            'fig_num',
            'img_url'
        ]
    ).to_numpy()

    with tqdm(total=len(data)) as pbar:
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            futures = executor.map(lambda d: download(*d), data)
            [pbar.update(1) for _ in futures]
    
    # cleanup 
    # os.removedirs(CSV_PATH)
    
    print('Finished!')

def download(fig_id: str, url: str) -> None:
    global downloaded 

    if f'{fig_id}.jpg' in downloaded:
        return # no need to download it again 
    
    response: requests.Response = requests.get(url,stream=True) 
    if response.status_code != 200:
        return # silent skip if we hit something like 404 not found 
    
    try:
        img = Image.open(BytesIO(response.content))
        img = ImagePreprocessor.format(img)
        ImagePreprocessor.save_to(img, f'{MINIFIG_DATA_PATH}/{fig_id}.jpg')
    except OSError:
        return # OSError: cannot write mode RGBA as JPEG
            
if __name__ == '__main__':
    main()