import json
import os

import requests
from dotenv import load_dotenv

from operategpt.providers.base import T2VPrompt

load_dotenv(verbose=True, override=True)

T2V_PROXY_URL = os.getenv("T2V_PROXY_URL")
T2V_GENERATE_VIDEO_API = "/generate_video"


def t2v_request(t2v_prompt: T2VPrompt):
    url = T2V_PROXY_URL + T2V_GENERATE_VIDEO_API
    headers = {"Content-Type": "application/json"}
    t2v_prompt_json = {
        "prompt": t2v_prompt.prompt,
        "num_inference_steps": 25,
        "height": 320,
        "width": 480,
        "num_frames": 24,
    }
    response = requests.post(url, headers=headers, data=json.dumps(t2v_prompt_json))
    result = response.json()

    if result.get("success"):
        return result["msg"]
    return None


if __name__ == "__main__":
    prompt = T2VPrompt()
    prompt.prompt = "A beautiful girl walks through the mall with a cup of milk tea, her hair blowing in the wind"
    print(t2v_request(prompt))
