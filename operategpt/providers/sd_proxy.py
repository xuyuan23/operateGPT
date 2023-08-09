import json
import os

import requests
from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

SD_PROXY_URL = os.getenv("SD_PROXY_URL")
SD_GENERATE_IMG_API = "/generate_img"


def sd_request(prompt: str, image_name: str):
    url = SD_PROXY_URL + SD_GENERATE_IMG_API
    headers = {"Content-Type": "application/json"}

    data = {"prompt": prompt, "image_name": image_name, "image_type": "png"}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()

    if result.get("success"):
        download_url = result["msg"].replace("downloadUrl= ", "")
        return download_url
    return None


if __name__ == "__main__":
    prompt = "A beautiful cat, Gorgeous, Elegant, Graceful, Radiant, Stunning, Alluring, Enchanting, Captivating, Mesmerizing, Lovely, Exquisite, Charming, Delicate, Sophisticated, Glamorous, Dazzling, Angelic, Ethereal, Breath-taking"
    image_name = "cat"
    print(sd_request(prompt=prompt, image_name=image_name))
