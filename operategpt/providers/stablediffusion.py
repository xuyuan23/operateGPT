import os
import time

import torch
import uvicorn
from diffusers import DiffusionPipeline
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

app = FastAPI()

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(ROOT_PATH, "data")
MODEL_PATH = os.path.join(ROOT_PATH, "models")
SD_MODEL = os.getenv("SD_MODEL", "stable-diffusion-xl-base-1.0")

pipe = DiffusionPipeline.from_pretrained(
    os.path.join(MODEL_PATH, SD_MODEL),
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16",
)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe.to(device)


class SDPrompt(BaseModel):
    prompt: str = None
    image_name: str = None
    image_type: str = "png"


@app.post("/generate_img")
def sd_request(sd_prompt: SDPrompt):
    prompt = sd_prompt.prompt
    image_name = sd_prompt.image_name
    image_type = sd_prompt.image_type
    try:
        if image_name is None:
            raise Exception("input param 'image_name' should not be empty!")

        image = pipe(prompt=prompt).images[0]
        tmp_dir = create_tmp_folder()
        img_name = f"{image_name}.{image_type}"
        img_path = os.path.join(tmp_dir, img_name)
        image.save(img_path)
        return {"success": True, "msg": f"downloadUrl= {img_path}"}
    except Exception as e:
        return {"success": False, "msg": f"generate image error: {str(e)}"}


def create_tmp_folder():
    timestamp = int(time.time())
    folder_name = os.path.join(DATA_PATH, str(timestamp))
    if os.path.exists(folder_name):
        raise Exception(f"folder {folder_name} was existed!")
    else:
        os.mkdir(folder_name)
    return folder_name


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")
