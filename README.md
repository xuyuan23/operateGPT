# OperateGPT: Revolutionize Your Operations with One-Line Requests


<div align="center">
  <p>
    <a href="https://github.com/xuyuan23/operateGPT">
        <img alt="stars" src="https://img.shields.io/github/stars/xuyuan23/operategpt?style=social" />
    </a>
    <a href="https://github.com/xuyuan23/operateGPT">
        <img alt="forks" src="https://img.shields.io/github/forks/xuyuan23/operategpt?style=social" />
    </a>
    <a href="https://opensource.org/licenses/MIT">
      <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
    </a>
    <a href="https://opensource.org/licenses/MIT">
      <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
    </a>
     <a href="https://github.com/xuyuan23/operateGPT/releases">
      <img alt="Release Notes" src="https://img.shields.io/github/release/xuyuan23/operateGPT" />
    </a>
    <a href="https://github.com/xuyuan23/operateGPT/issues">
      <img alt="Open Issues" src="https://img.shields.io/github/issues-raw/xuyuan23/operateGPT" />
    </a>
    <a href="https://codespaces.new/xuyuan23/operateGPT">
      <img alt="Open in GitHub Codespaces" src="https://github.com/codespaces/badge.svg" />
    </a>
  </p>

[**简体中文**](docs/zh/README_ZH.md) |[**Documents**](http://operategpt.cn/docs/category/docen)|[**WebSite**](http://operategpt.cn/)
</div>

<a href="http://dev.operategpt.cn">🚀🚀Experience Now!!</a>

[🔥🔥Latest Release Version:V0.0.1](docs/en/OperateGPT.md)

[🔥🔥Multi-Models Management](docs/en/multi_models_manage.md)


Using large language models and multi-agent technology, a single request can automatically generate marketing copy, images, and videos, and with one click, can be sent to multiple platforms, achieving a rapid transformation in marketing operations.

![OperateGPT Process](assets/operateGPT_process.png)

## Supported LLMs

| LLM             | Supported    | Model Type  | Notes    |
|-----------------|--------------|-------------|----------|
| ChatGPT         | ✅            | Proxy       | Default  |
| Bard            | ✅            | Proxy       |          |
| Vicuna-13b      | ✅            | Local Model |          |
| Vicuna-13b-v1.5 | ✅            | Local Model |          |
| Vicuna-7b       | ✅            | Local Model |          |
| Vicuna-7b-v1.5  | ✅            | Local Model |          |
| ChatGLM-6B      | ✅            | Local Model |          |
| ChatGLM2-6B     | ✅            | Local Model |          |
| baichuan-13b    | ✅            | Local Model |          |
| baichuan2-13b   | ✅            | Local Model |          |
| baichuan-7b     | ✅            | Local Model |          |
| baichuan2-7b    | ✅            | Local Model |          |
| Qwen-7b-Chat    | Coming soon  | Local Model |          |

## Supported Embedding Models

| LLM                    | Supported | Notes   |
|------------------------|-----------|---------|
| sentence-transformers  | ✅         | Default |
| text2vec-large-chinese | ✅         |         |
| m3e-large              | ✅         |         |
| bge-large-en           | ✅         |         |
| bge-large-zh           | ✅         |         |


## Installation

Firstly, download and install the relevant LLMs.

```commandline
mkdir models & cd models

# Size: 522 MB
git lfs install 
git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

# [Optional]
# Size: 94 GB, supported run in cpu model(RAM>14 GB). stablediffusion-proxy service is recommended, https://github.com/xuyuan23/stablediffusion-proxy
git lfs install 
git clone https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

# [Optional]
# Size: 16 GB, supported run in cpu model(RAM>16 GB). Text2Video service is recommended. https://github.com/xuyuan23/Text2Video
git lfs install
git clone https://huggingface.co/cerspense/zeroscope_v2_576w
```

Then, download dependencies and launch your project.
```commandline
yum install gcc-c++
pip install -r requirements.txt

# copy file `.env.template` to new file `.env`, and modify the params in `.env`.
cp .env.template .env 

[Options]
# deploy stablediffusion service, if StableDiffusion proxy is used, no need to execute it!
python operategpt/providers/stablediffusion.py

[Options]
# deploy Text2Video service, if Text2Video proxy server is used, no need to execute it!
python operategpt/providers/text2video.py

# Quick trial: two params: idea and language, `en is default`, also supported zh(chinese).
python main.py "Prepare a travel plan to Australia" "en"
```

## Configuration
- By default, ChatGPT is used as the LLM, and you need to configure the `OPEN_AI_KEY` in `.env`

```properties
OPEN_AI_KEY=sk-xxx

# If you don't deploy stable diffusion service, no image will be generated.
SD_PROXY_URL=127.0.0.1:7860

# If you don't deploy Text2Video service, no videos will be generated.
T2V_PROXY_URL=127.0.0.1:7861
```
- More Details see file `.env.template`

## Generated DEMOs

- [What is DB-GPT?](docs/example/what_is_dbgpt.md)

- [Travel to Chengdu](docs/example/travel_to_chengdu.md)

- [Jingnu teaching design?](docs/example/jingnu_teaching_design.md)

