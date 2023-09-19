import json
import os
import random
import sys
from enum import Enum
from typing import Dict, List

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_PATH)
from operategpt.llms.worker.worker import Worker, WorkerConnection, LLMReq

load_dotenv(verbose=True, override=True)

LLM_SERVER_PORT = int(os.getenv("LLM_MANAGE_SERVER_PORT", 8007))

app = FastAPI()


class LLMWorkerReqParam(Enum):
    """
    when register llm worker, you should replace the key variable as below.
    """

    USER_PROMPT = "{USER_PROMPT}"
    MODEL_TEMPERATURE = "{MODEL_TEMPERATURE}"
    MODEL_NAME = "{MODEL_NAME}"


class WorkerManager:

    """
    worker manager: manage llm workers.
    support multiply threads request
    """

    __instance = None

    @staticmethod
    def get_instance():
        if not WorkerManager.__instance:
            WorkerManager.__instance = WorkerManager()
        return WorkerManager.__instance

    def __init__(self):
        self.workers: Dict[str, List["Worker"]] = {}

    def add_worker(self, worker: Worker):
        if worker.model_name not in self.workers:
            self.workers[worker.model_name] = []
        self.workers[worker.model_name].append(worker)

    def remove_worker(self, conn: WorkerConnection):
        if not conn.model_name:
            return {
                "success": False,
                "msg": "remove worker error: conn.model_name cannot be empty",
            }
        if not conn.req_url_template:
            return {
                "success": False,
                "msg": "remove worker error: conn.req_url_template cannot be empty",
            }

        to_remove_worker = None
        for model_name, worker_list in self.workers.items():
            if model_name != conn.model_name:
                continue
            for worker in worker_list:
                if (
                    worker.model_name == conn.model_name
                    and worker.conn
                    and worker.conn.req_url_template == conn.req_url_template
                ):
                    to_remove_worker = worker
                    break
            if to_remove_worker:
                worker_list.remove(to_remove_worker)
        if not to_remove_worker:
            return {"success": False, "msg": "No llm worker to remove."}
        return {
            "success": True,
            "msg": f"remove llm worker(model_name={conn.model_name}, url={conn.req_url_template}) succeed!",
        }

    def get_workers_by_type(self, model_name: str):
        return self.workers.get(model_name, [])

    def get_all_workers(self):
        return self.workers

    def exec(self, req: LLMReq):
        """
        Execute llm inference, choose llm execute:
        More: record the execute status, if failed we should alter the developer or remove the llm server from manager.
        :param req: llm request
        :return: execute result.
        """

        if not req.model_name:
            raise ValueError("the request model_name cannot be empty")
        worker_list = self.workers.get(req.model_name)
        if not worker_list:
            raise f"The request model({req.model_name}) not exist in llm worker manager"
        worker: Worker = get_random_element(worker_list)

        try:
            if not worker.conn:
                raise f"Worker(model_name={req.model_name}) exist an empty connection"

            if not worker.conn.req_type:
                raise f"the req_type(GET/POST) can not be empty"

            if worker.conn.req_type == "GET":
                response = requests.get(
                    worker.conn.req_url_template, headers=worker.conn.header
                )
            elif worker.conn.req_type == "POST":
                response = requests.post(
                    worker.conn.req_url_template,
                    headers=worker.conn.header,
                    data=parse_req_body(worker.conn.body, req),
                )
            else:
                raise f"model request type ({worker.conn.req_type}) was not supported"
            return {
                "success": True,
                "msg": "execute succeed",
                "result": get_from_resp(response, worker.conn.response_extract),
            }
        except Exception as e:
            msg = f"worker execute error: {str(e)}"
            print(msg)
            return {"success": False, "msg": msg}


def parse_req_body(req_body: dict, req: LLMReq):
    """
    Replace request content.
    :param req_body:
    :param req:
    :return:
    """
    for key, value in req_body.items():
        if isinstance(value, str):
            req_body[key] = value.replace(
                LLMWorkerReqParam.USER_PROMPT.value, req.input
            ).replace(LLMWorkerReqParam.MODEL_NAME.value, req.model_name)
    return json.dumps(req_body)


def get_from_resp(response, response_extract: str) -> str:
    """
    Extract data from response by response_extract
    :param response:
    :param response_extract:
    :return:
    """
    if not response_extract:
        return str(response.text)
    response_json = response.json()
    array = response_extract.split(".")
    data = response_json
    for item in array:
        if "[]" in item:
            key = item.split("[]")
            data = data[key[0]][0]
        else:
            data = data[item]
    return str(data)


def get_random_element(arr):
    """
    Get a random element from arr.
    :param arr:
    :return:
    """
    if not arr:
        return None
    return random.choice(arr)


@app.post("/api/server/register")
def register(conn_dict: dict) -> dict:
    conn: WorkerConnection = WorkerConnection(**conn_dict)
    manager: WorkerManager = WorkerManager.get_instance()
    for model_name, worker_list in manager.workers.items():
        for worker in worker_list:
            if (
                worker.model_name == conn.model_name
                and worker.conn
                and worker.conn.req_url_template == conn.req_url_template
            ):
                return {
                    "success": False,
                    "msg": f"LLM(model_name({conn.model_name}), url={conn.req_url_template}) has registered!",
                }

    manager: WorkerManager = WorkerManager.get_instance()
    worker: Worker = Worker(model_name=conn.model_name, conn=conn)
    manager.add_worker(worker)
    return {"success": True, "msg": f"register LLM {conn.model_name} succeed!"}


@app.post("/api/v1/chat/completions")
def chat(req: LLMReq):
    return WorkerManager.get_instance().exec(req)


@app.post("/api/server/offline")
def chat(conn_dict: dict):
    conn: WorkerConnection = WorkerConnection(**conn_dict)
    return WorkerManager.get_instance().remove_worker(conn)


@app.post("/api/server/workers")
def workers():
    wk_map: Dict[str, List["Worker"]] = WorkerManager.get_instance().get_all_workers()

    wks: List[Dict] = []
    for model_name, worker_list in wk_map.items():
        for worker in worker_list:
            wk = {
                "model_name": worker.model_name,
                "req_url_template": worker.conn.req_url_template,
            }
            wks.append(wk)

    return {"success": True, "data": str(wks)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=LLM_SERVER_PORT, log_level="info")
