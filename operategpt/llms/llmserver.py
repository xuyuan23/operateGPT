import os
import sys
from typing import List
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_PATH)

from operategpt.llms.worker.worker import Worker, LLMReq
from operategpt.llms.llm_out.model_output import ModelOutput
from operategpt.llms.message.base_message import ModelMessage

load_dotenv(verbose=True, override=True)
LLM_NAME = os.getenv("LLM_NAME", "proxyllm")
OPEN_AI_PROXY_SERVER_URL = os.getenv("OPEN_AI_PROXY_SERVER_URL")
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
LLM_SERVER_PORT = int(os.getenv("LLM_SERVER_PORT"))

app = FastAPI()
worker: Worker = Worker(LLM_NAME)


@app.post("/api/generate")
def gen(req: LLMReq):
    print(f"input={req.input}")
    msg: ModelMessage = ModelMessage(role="human", content=req.input)
    messages: List[ModelMessage] = list([msg])
    params = {
        "model": worker.model_name,
        "prompt": f"human:{req.input}###",
        "messages": messages,
        "temperature": 0.6,
        "max_new_tokens": 1024,
        "stop": "###",
        "echo": False,
    }

    model_output = None
    previous_response = ""
    for output in worker.generate_stream_func(
        worker.model, worker.tokenizer, params, "cuda", context_len=2048
    ):
        incremental_output = output[len(previous_response) :]
        print(incremental_output, end="", flush=True)
        previous_response = output
        model_output = ModelOutput(text=output, error_code=0, model_context={})
    print(f"\ndata: {str(model_output)}")
    return previous_response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=LLM_SERVER_PORT, log_level="info")
