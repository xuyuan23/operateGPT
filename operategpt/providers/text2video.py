import os
import time

import torch
import uvicorn
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video
from fastapi import FastAPI
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydantic import BaseModel

app = FastAPI()

T2V_MODEL = os.getenv("T2V_MODEL")

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(ROOT_PATH, "data")
MODEL_PATH = os.path.join(ROOT_PATH, "models")

pipe = DiffusionPipeline.from_pretrained(
    os.path.join(MODEL_PATH, T2V_MODEL), torch_dtype=torch.float16
)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_model_cpu_offload()


class LLMPrompt(BaseModel):
    prompt: str = None
    num_inference_steps: int = 40
    height: int = 320
    width: int = 576
    num_frames: int = 24


@app.post("/generate_video")
def generate_video(lp: LLMPrompt):
    video_frames = pipe(
        lp.prompt, lp.num_inference_steps, lp.height, lp.width, lp.num_frames
    ).frames
    timestamp = int(time.time())
    video_name_tmp = f"{T2V_MODEL}_{str(timestamp)}_tmp.mp4"
    video_path = export_to_video(video_frames, os.path.join(DATA_PATH, video_name_tmp))
    video = VideoFileClip(video_path)

    video_name = f"{T2V_MODEL}_{str(timestamp)}.mp4"
    output_video_path = os.path.join(DATA_PATH, video_name)
    video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
    return output_video_path


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7861, log_level="info")
