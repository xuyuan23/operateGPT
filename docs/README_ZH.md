# OperateGPT: 一句话需求即可完成运营的变革
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

[**English**](../README.md) |[**文档**](http://operategpt.cn/web/#/602177878/152973408)|[**网站首页**](http://operategpt.cn/)
</div>

<a href="http://dev.operategpt.cn">🚀🚀立刻体验！！</a>

[🔥🔥最新发布版本:V0.0.1](./operategpt_release_doc_zh.md)

- 利用大语言模型和多智能体技术，通过一行需求自动生成运营文案、图片和视频，一键发送多个平台实现快速运营的变革

![OperateGPT Process](../assets/operateGPT_process.png)


## 支持的运营平台

| Operate Platform | Supported   | API           | Notes |
|------------------|-------------|---------------|-------|
| YouTube          | Coming soon | Coming soon   |       |
| Twitter          | Coming soon | Coming soon   |       |
| CSDN             | Coming soon | Coming soon   |       |
| B站               | Coming soon | Coming soon   |       |
| 知乎               | Coming soon | Coming soon   |       |
| 微信               | Coming soon | Coming soon   |       |
| 豆瓣               | Coming soon | Coming soon   |       |
| 抖音               | Coming soon | Coming soon   |       |

## 支持的大语言模型

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

## 支持的文本嵌入模型

| LLM                    | Supported | Notes   |
|------------------------|-----------|---------|
| sentence-transformers  | ✅         | Default |
| text2vec-large-chinese | ✅         |         |
| m3e-large              | ✅         |         |
| bge-large-en           | ✅         |         |
| bge-large-zh           | ✅         |         |


## 安装

首先，下载相关模型
```commandline
mkdir models & cd models

# 下载embedding 模型，默认all-MiniLM-L6-v2，对于中文可以使用text2vec-large-chinese
git lfs install 
git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

# 下载stabediffusion模型 (git仓库94GB，模型47GB), 推荐使用stablediffusion-proxy, 参考 https://github.com/xuyuan23/stablediffusion-proxy
git lfs install 
git clone https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
```

下载安装python项目依赖包，并启动项目

``` commandline
# 安装python依赖包
pip install -r requirements.txt

# 复制.env.template文件内容到新创建的.env文件中，并修改.env文件中的内容
cp .env.template .env 

# 启动stablediffusion服务, 如果使用了StableDiffusion代理，则无需执行!
python operategpt/providers/stablediffusion.py

# 执行项目，将会生成一个markdown文件 /data/operation_data/xxx.md
python main.py "what is MetaGPT?"
```

## 配置
- 默认使用ChatGPT作为LLM, 首先你应该在`.env`中设置`OPEN_AI_KEY`， StableDiffusion使用代理则需要设置，否则需要在本地启动

```properties
OPEN_AI_KEY=sk-xxx

# 如果你没有部署StableDiffusion，则无法生成图像
SD_PROXY_URL=127.0.0.1:7860
```

## Video Demo

https://github.com/xuyuan23/operateGPT/assets/26043513/bd585d00-f793-443d-a395-532d0c038e97