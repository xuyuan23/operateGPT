# Multi-model management

![OperateGPT](../../assets/operategpt_logo.png)

## 1. Why do we need multi-model management?
In the era of flourishing LLMs (Large Language Models), a large number of models have emerged. These models include not only large language models, but also various image generation models, video generation models, and even multimodal models. In a project, it is unlikely to have just one type of model, let alone only one model. It is more likely to have complex combinations such as x LLM_A models, y LLM_B models, and z LLM_C models. In real-world business scenarios, there will be a multitude of problems to be solved.
- How to implement multiple model scheduling?
- How to achieve load balancing?
- How to manage the health of inference services?
- How to quickly integrate third-party models?
- How to achieve fast sharing of models without the need for adaptation?
- How to...

The emergence of multi-model management is driven by a multitude of scenarios and demands.


## 2. Architecture

### 2.1 Current status of multi-models

- Currently, the better private large language models include the Llama series, ChatGLM series, and Baichuan series. As for commercial large models such as ChatGPT, Bard, and Claude, the inference cost is lower than that of privately deployed models and far superior to privately deployed models. Users can also access them in a lightweight manner through proxies.


- Currently, there are some image models that perform well, such as the commercial model Midjourney and the open-source model StableDiffusion. The latest StableDiffusion model has parameters of nearly 50GB and supports inference on 8GB GPUs, although CPU inference is slower.


- Currently, the commercial model Gen-2 performs well in video modeling. Other open-source video models have relatively poor performance. With the high attention given to multimodal models, progress is being made rapidly, and the performance is continuously improving.

### 2.2 Characteristics of large AI models

Deploying private inference services can be costly, often requiring dozens of gigabytes of memory and GPU memory. Multi-model deployment is typically managed through service APIs, and commercial large models are also accessed through APIs. Therefore, it is entirely feasible to build a multi-model management system based on inference service APIs.

### 2.3 Multi-model management architecture

<img src="../../assets/multi_llms_manage.png" alt="Multi-Model-Management"/>


## 3. Multi-model management API

### 3.0 Launch Services

- Portable code module point [here](../../operategpt/llms)

```commandline

# Inference model service configuration, .env file
# If you are deploying a private model locally, set it as follows: LLM_NAME=chatglm2-6b
# If you are using a proxy model like ChatGPT, configure it as follows:
LLM_NAME=proxyllm
OPEN_AI_PROXY_SERVER_URL=https://api.openai.com/v1/chat/completions
OPEN_AI_KEY=sk-xxx

# Configure server ports, default inference service port is 8008, LLM management service port is 8007. You can start multiple inference services (llmserver) and register them with the management service.
LLM_SERVER_PORT=8008
LLM_MANAGE_SERVER_PORT=8007

# Start the model management service (you can also bind the API to your own application service)
python operategpt/llms/worker_manager.py

# [Optional if you already have a model service] Start the model service, you need to configure some related parameters, refer to the model_config.py file
python operategpt/llms/llmserver.py
```



### 3.1 Model Registration
- Model registration requires registering the API with the LLM framework service for management. The key parameters in the registration need to be selectively replaced, usually only requiring the replacement of {USER_PROMPT}.

```commandline
response_extract: Use the form response["a"]["b"][0]["c"] to extract values from the response.
owner is the owner of the model.
req_url_template is the URL template for the inference service.
model_name is the name of the model. If there are multiple models with the same name, they will be called in a load-balanced manner.
body is the request body.
When registering a model, you need to modify some parameters of the model request to the corresponding values of the following enumeration class. {USER_PROMPT} is a required mapping, while others are optional:
    USER_PROMPT = "{USER_PROMPT}"
    MODEL_TEMPERATURE = "{MODEL_TEMPERATURE}"
    MODEL_NAME = "{MODEL_NAME}"
```

Example: Registering an Inference Service for a Large Model with the Model Manager:
```commandline

# Initiate Registration Request
curl -X POST -H "Content-Type: application/json" -d '{
    "model_name": "chatglm2-6b",
    "body": {
        "input": "{USER_PROMPT}",
        "model_name": "{MODEL_NAME}"
    },
    "req_url_template": "http://127.0.0.1:8008/api/generate",
    "owner": "operategpt",
    "response_extract": ""
}' http://127.0.0.1:8007/api/server/register


# Return Result
{
    "success": true,
    "msg": "register LLM proxyllm succeed!"
}

```

If your LLM response result is json-format data, you should provide the method to extract the real result, for example:
```
{
  "code": "200",
  "data": {
    "items": [
      {
        "attributes": {
          "answer": "I am ChatGLM2-6B ..."
        }
      }
    ]
  },
  "success": true,
  "traceId": "0b46977c16953709036745431ea818"
}
```

> response_extract = "data.items[].attributes.answer"



### 3.2 Query models

```commandline

# 查询请求
curl http://127.0.0.1:8007/api/server/workers

# Return Result

{
    "success": true,
    "data": [
    	{"model_name": "chatglm2-6b", "req_url_template": "https://xxx/openapi/xxx/inference/query"}, 
    	{"model_name": "proxyllm", "req_url_template": "http://localhost:8008/generate"}
    ]
}

```


### 3.3 Offline Model

```commandline

# Initiate Offline Request
curl -X POST -H "Content-Type: application/json" -d '{
    "model_name": "chatglm2-6b",
    "req_url_template": "http://127.0.0.1:8008/api/generate"
}' http://127.0.0.1:8007/api/server/offline


# Return Result
{
    "success": true,
    "msg": "remove llm worker(model_name=chatglm2-6b, url=http://127.0.0.1:8008/api/generate) succeed!"
}
```


### 3.4 Model Inference

```commandline

# Model Request1
curl -X POST -H "Content-Type: application/json" -d '{
    "input": "who are you?",
    "model_name": "chatglm2-6b"
}' http://127.0.0.1:8007/api/v1/chat/completions

# Return Result1
{
    "success": true,
    "msg": "execute succeed",
    "result": "Hey there! My name is Noxix, and I am an AI chatbot designed to have conversations with users like you. How can I assist you today?"
}



# Model Request2
curl -X POST -H "Content-Type: application/json" -d '{
    "input": "who are you?",
    "model_name": "proxyllm"
}' http://127.0.0.1:8007/api/v1/chat/completions

# Return Result2
{
    "success": true,
    "msg": "execute succeed",
    "result": "I am an AI language model developed by OpenAI. I am programmed to provide information and assist with various tasks. How can I help you today?"
}

```

## 4. Code

[OperateGPT Multi-Model Management's llms directory](https://github.com/xuyuan23/operateGPT/tree/master/operategpt/llms)
