from pydantic import BaseModel


class T2VPrompt(BaseModel):
    prompt: str = None
    num_inference_steps: int = 40
    height: int = 320
    width: int = 576
    num_frames: int = 24


class T2ImgPrompt(BaseModel):
    prompt: str = None
    image_name: str = None
    image_type: str = "png"
