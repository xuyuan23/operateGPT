import json
from typing import List

import requests

from operategpt.llms.llm_out.proxy.proxy_model import ProxyModel
from operategpt.llms.message.base_message import ModelMessage, ModelMessageRoleType


def chatgpt_generate_stream(
    model: ProxyModel, tokenizer, params, device, context_len=2048
):
    history = []
    model_params = model.get_params()

    proxy_api_key = model_params.proxy_api_key
    proxy_server_url = model_params.proxy_server_url
    proxyllm_backend = model_params.proxyllm_backend
    if not proxyllm_backend:
        proxyllm_backend = "gpt-3.5-turbo"

    headers = {
        "Authorization": "Bearer " + proxy_api_key,
        "Token": proxy_api_key,
    }

    messages: List[ModelMessage] = params["messages"]
    for message in messages:
        if message.role == ModelMessageRoleType.HUMAN:
            history.append({"role": "user", "content": message.content})
        elif message.role == ModelMessageRoleType.SYSTEM:
            history.append({"role": "system", "content": message.content})
        elif message.role == ModelMessageRoleType.AI:
            history.append({"role": "assistant", "content": message.content})
        else:
            pass

    temp_his = history[::-1]
    last_user_input = None
    for m in temp_his:
        if m["role"] == "user":
            last_user_input = m
            break
    if last_user_input:
        history.remove(last_user_input)
        history.append(last_user_input)

    payloads = {
        "model": proxyllm_backend,
        "messages": history,
        "temperature": params.get("temperature"),
        "max_tokens": params.get("max_new_tokens"),
        "stream": True,
    }

    res = requests.post(proxy_server_url, headers=headers, json=payloads, stream=True)

    print(f"Send request to {proxy_server_url} with real model {proxyllm_backend}")

    text = ""
    for line in res.iter_lines():
        if line:
            if not line.startswith(b"data: "):
                error_message = line.decode("utf-8")
                yield error_message
            else:
                json_data = line.split(b": ", 1)[1]
                decoded_line = json_data.decode("utf-8")
                if decoded_line.lower() != "[DONE]".lower():
                    obj = json.loads(json_data)
                    if obj["choices"][0]["delta"].get("content") is not None:
                        content = obj["choices"][0]["delta"]["content"]
                        text += content
                yield text
