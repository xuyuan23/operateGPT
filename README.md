# OperateGPT: Taking Your Operations to the Next Level with Automation
- Revolutionize Your Operations with One Sentence Automation: Utilizing large language models and multi-agents to generate operational copy, images, and videos with one-line requirements.

![A software company consists of LLM-based roles](assets/OperateGPT_arch.png)


## Supported Platform

| Operate Platform | Supported   | API           | Notes |
|------------------|-------------|---------------|-------|
| YouTube          | Coming soon | Coming soon   |       |
| Twitter          | Coming soon | Coming soon   |       |
| CSDN             | Coming soon | Coming soon   |       |
| Bilibili         | Coming soon | Coming soon   |       |
| Zhihu            | Coming soon | Coming soon   |       |
| Wechat           | Coming soon | Coming soon   |       |
| Douban           | Coming soon | Coming soon   |       |
| TikTok           | Coming soon | Coming soon   |       |

## Supported LLMs

| LLM             | Supported    | Model Type   | Notes |
|-----------------|--------------|--------------|-------|
| ChatGPT         | Yes          | Proxy        |       |
| Bard            | Yes          | Proxy        |       |
| Claude          | Coming soon  | Proxy        |       |
| Vicuna-13b-v1.5 | Coming soon  | Local Model  |       |
| ChatGLM2-6B     | Coming soon  | Local Model  |       |
| Qwen-7b-Chat    | Coming soon  | Local Model  |       |

## Supported Embedding Models

| LLM                      | Supported    | Notes |
|--------------------------|--------------|-------|
| all-MiniLM-L6-v2         | Yes          |       |
| text2vec-large-chinese   | Coming soon  |       |


## Quick Start

Firstly, download relative LLMs.
```commandline
# download embedding model
git lfs install 
git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

# download stable diffusion model
git lfs install 
git clone https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

```

Then, download dependencies and launch your project.
```commandline

# create some directories
mkdir models
mkdir data
mkdir logs

# install python dependencies
pip install -r requirements.txt

# copy file `.env.template` to new file `.env`, and modify the params in `.env`.
copy .env.template .env 

# deploy stablediffusion service, stablediffusion-proxy service is recommended. 
# see doc http://operategpt.cn/web/#/p/9cfc5cffa5120f8a520573f092f436d1
python operategpt/provider/stablediffusion.py

# execute project, generate file /data/operation_data/xxx.md
python demo.py "what is MetaGPT?"
```

Note: maybe you should execute command `export OPENAI_API_KEY="sk-..."` to config your OPEN-AI-KEY Firstly.


## Display
- The content is fully generated by OperateGPT: http://operategpt.cn/web/#/602177878/0

- Video DEMO

https://github.com/xuyuan23/operateGPT/assets/26043513/bd585d00-f793-443d-a395-532d0c038e97