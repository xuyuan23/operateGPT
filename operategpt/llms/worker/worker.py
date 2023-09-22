import os
from enum import Enum
from typing import Any

from pydantic import BaseModel

from operategpt.llms.llm_out.chat_adapter import get_llm_chat_adapter
from operategpt.llms.llm_out.proxy.proxy_model import ProxyModel
from operategpt.llms.model_config import LLM_MODEL_CONFIG, get_device
from operategpt.llms.model_loader import ModelLoader
from operategpt.llms.parameter import ModelParameters, ProxyModelParameters
from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)
LLM_NAME = os.getenv("LLM_NAME", "proxyllm")
OPEN_AI_PROXY_SERVER_URL = os.getenv("OPEN_AI_PROXY_SERVER_URL")
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")


class LLMWorkerType(Enum):
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"


class WorkerConnection:
    """
    Worker connection, request body see worker_manager.LLMWorkerReqParam, replace request format.

    Extract response result from the API:
      if None:

      else if "a.b[].c":
        res['a'].['b'](0).c
    """

    def __init__(
        self,
        model_name: str,
        req_type: str = "POST",
        req_url_template: str = "http://localhost:8008/api/generate",
        req_param: dict = None,
        is_stream: bool = False,
        header: dict = None,
        body: dict = None,
        owner: str = None,
        worker_type: str = LLMWorkerType.REMOTE.name,
        response_extract: str = None,
        **data: Any
    ):
        super().__init__(**data)
        self.model_name = model_name
        self.req_type = req_type
        self.req_url_template = req_url_template
        self.req_param: dict = req_param
        self.is_stream = is_stream
        self.header = header
        self.body = body
        self.owner = owner
        self.worker_type = worker_type
        self.response_extract = response_extract


class Worker:
    """
    LLM Worker, support multiply workers work together.
    """

    def __init__(self, model_name, conn: WorkerConnection = None):
        if not model_name:
            raise ValueError("model_name cannot be empty!")

        self.model_name = model_name
        if not conn:
            self.conn = WorkerConnection(
                model_name=self.model_name,
                owner="OperateGPT",
                body={},
                worker_type=LLMWorkerType.LOCAL.name,
            )
            self.model_path = LLM_MODEL_CONFIG.get(model_name)
            if self.model_path.endswith("/"):
                self.model_path = self.model_path[:-1]
            ml: ModelLoader = ModelLoader(
                model_path=self.model_path, model_name=model_name
            )
            mp: ModelParameters = ModelParameters(
                model_name=model_name, model_path=self.model_path, device=get_device()
            )
            self.model, self.tokenizer = ml.loader_with_params(mp)

            self.llm_chat_adapter = get_llm_chat_adapter(model_name, self.model_path)
            self.generate_stream_func = self.llm_chat_adapter.get_generate_stream_func(
                self.model_path
            )
            if "proxyllm" in model_name:
                self.model: ProxyModel = ProxyModel(
                    ProxyModelParameters(
                        device="cpu",
                        max_context_size=4096,
                        model_name=self.model_name,
                        model_path=self.model_path,
                        proxy_api_key=OPEN_AI_KEY,
                        proxy_server_url=OPEN_AI_PROXY_SERVER_URL,
                    )
                )
        else:
            if not conn.worker_type:
                raise ValueError("worker_type cannot be empty.")
            self.conn = conn


class LLMReq(BaseModel):
    input: str
    model_name: str = LLM_NAME
