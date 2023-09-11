import json
import os
import time

from googlesearch import search
import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv

from operategpt.embeddings import EmbeddingEngine, KnowledgeType
from operategpt.logs import logger
from operategpt.providers import sd_proxy
from operategpt.providers.base import T2VPrompt
from operategpt.providers.text2video_proxy import t2v_request

load_dotenv(verbose=True, override=True)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DATA_PATH = os.path.join(ROOT_DIR, "data")
KNOWLEDGE_UPLOAD_ROOT_PATH = os.path.join(PROJECT_DATA_PATH, "vectordb")
GENERATED_OPERATE_DATA = os.path.join(PROJECT_DATA_PATH, "operation_data")

OPEN_AI_PROXY_SERVER_URL = os.getenv(
    "OPEN_AI_PROXY_SERVER_URL", "https://api.openai.com/v1/chat/completions"
)
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "Chroma")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", GENERATED_OPERATE_DATA)
GENERATED_OPERATE_DATA_DEFAULT_DIR = os.getenv("GENERATED_OPERATE_DATA_DEFAULT_DIR", "/var/www/html/experience")


OPERATE_PROMPT = """You are an operation expert, now please write a detailed operation article according to the following content, the format is beautiful and the content is attractive. Remarks: Be sure to author and analyze according to the content provided, the author is OperateGPT, and may include charts as appropriate, generate in Markdown format, the author operateGPT should be linked to 'https://github.com/xuyuan23/operateGPT'.
content: 
```
{0}
```

To make the operational document appear more organized, please insert the following images at the different appropriate locations in the document, not the same locations, you can use the format such as `<img src='http://xxxxxxx.png'/>`, if the image list is empty, please ignore.
```
{1}
```

Please insert the following videos at the different appropriate locations in the document, not the same locations, you can use the format such as `<video width="640" height="360" controls> <source src="http://xxxxxx.mp4" type="video/mp4">video-name</video>`, if the video list is empty, please ignore.
```
{2}
```
"""

IMAGE_DESC_PROMPT = """Based on the content below, select 3 to 5 different relevant events or content information and describe them along with their respective characteristics with length of fewer than 100 words.:
```
{0}
```

Please provide an answer similar to the one below, but without any additional information, details start with <ImagePrompt>, end with </ImagePrompt>, no content beyound tag <ImagePrompt> and </ImagePrompt>. 
You should response me follow next format, only one json data with some key-value data:

<ImagePrompt> {{"picture-name-1": "<summary content1>", "picture-name-2": "<summary content2>", "picture-name-3": "<summary content3>"}} </ImagePrompt>

"""

VIDEO_DESC_PROMPT = """Based on the content below, summarize a core thing, as well as related functions and processes
```
{0}
```

Please provide an answer similar to the one below, but without any additional information, details start with <VideoPrompt>, end with </VideoPrompt>, no content beyound tag <VideoPrompt> and </VideoPrompt>. 
You should response me follow next format, only one json data with some key-value data:

<VideoPrompt> {{"video-name-1": "<summary content1>"}} </VideoPrompt>

"""


def search_relative_data_from_ds(query):
    """
    search the content and extract the text from html.
    :param query:
    :return:
    """
    search_results = search(query, num_results=5, lang="en")
    relevant_data = ""
    for result in search_results:
        try:
            logger.info(f"link:{result}")
            resp = requests.get(result, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            ans = soup.get_text().replace("\n", "").replace("\r", "").replace("\t", "")
            logger.info(f"website data:{ans}")
            relevant_data += ans
        except Exception as ex:
            logger.info(f"get link failed:{str(ex)}")
    return relevant_data if relevant_data != "" else query


def query_from_openai_proxy(prompt):
    headers = {
        "Authorization": "Bearer " + OPEN_AI_KEY,
        "Token": OPEN_AI_KEY,
    }

    history = [
        {
            "role": "system",
            "content": "You are OperateGPT, a large language model.",
        },
        {"role": "user", "content": prompt},
    ]
    payloads = {
        "model": "gpt-3.5-turbo",
        "messages": history,
        "temperature": 0.7,
        "stream": False,
    }

    res = requests.post(
        OPEN_AI_PROXY_SERVER_URL, headers=headers, json=payloads, stream=False
    )

    print(f"res={str(res)}")

    json_result = json.loads(res.text)

    return json_result["choices"][0]["message"]["content"]


def embedding_knowledge(content: str, vector_store_name: str):
    client = EmbeddingEngine(
        knowledge_source=content,
        knowledge_type=KnowledgeType.TEXT.value,
        model_name=ROOT_DIR + "/models/" + EMBEDDING_MODEL,
        vector_store_config={
            "vector_store_name": vector_store_name,
            "vector_store_type": VECTOR_STORE_TYPE,
            "chroma_persist_path": KNOWLEDGE_UPLOAD_ROOT_PATH,
        },
        text_splitter=None,
    )
    chunk_docs = client.read()
    client.knowledge_embedding_batch(chunk_docs)
    return client


def parse_image_info(summary_data: str) -> dict:
    images_prompt_info = IMAGE_DESC_PROMPT.format(summary_data)
    logger.info(
        f"\n====================================images_prompt_info=\n{images_prompt_info}"
    )

    image_info = query_from_openai_proxy(images_prompt_info)
    logger.info(f"\n====================================image_info=\n {image_info}")

    # Extract the content within the ImagePrompt tag
    start_index = image_info.index("<ImagePrompt>") + 13
    end_index = image_info.index("</ImagePrompt>")
    content = image_info[start_index:end_index]
    logger.info(
        f"\n=====================================extract json prompt from image_info=\n{content}"
    )

    data_dict = json.loads(content)
    converted_dict = {key.replace(" ", "_"): value for key, value in data_dict.items()}
    return converted_dict


def download_file(download_url: str) -> str:
    try:
        parts = download_url.rsplit('/', 2)
        origin_file = f'{parts[-2]}/{parts[-1]}'
        filename = f"{GENERATED_OPERATE_DATA_DEFAULT_DIR}/{origin_file}"
        os.makedirs(f"{GENERATED_OPERATE_DATA_DEFAULT_DIR}/{parts[-2]}", exist_ok=True)
        response = requests.get(download_url)

        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"download file success, filename={filename}")
            return f"{DOWNLOAD_FOLDER}/{origin_file}"
        else:
            print(f"download file error, HTTP state code: {response.status_code}")
            return ""
    except Exception as e:
        print(f"download file error: {str(e)}")


def generate_images(converted_dict: dict) -> str:
    image_dict = []
    try :
        if len(converted_dict) == 0:
            return "No images"
        index = 0
        logger.info(
            f"parse_image_info: start generate pictures, total: {len(converted_dict)}, current: {index}"
        )
        # start request stable diffusion:
        for image_name, image_prompt in converted_dict.items():
            index += 1
            download_url = sd_proxy.sd_request(prompt=image_prompt, image_name=image_name)
            # TODO download to local folder! (such as /var/www/html/xxx)
            # http://47.99.143.40/1693913288/DB_GPT_Features.png  TO  {BASEURL}/1693913288/DB_GPT_Features.png
            # If not deployed PROD, please delete the next line of code.
            download_url = download_file(download_url)

            image_dict.append({"image_name": image_name, "url": download_url})
            logger.info(
                f"parse_image_info: generating pictures, total: {len(converted_dict)}, completed: {index}, image_dict={str(image_dict)}"
            )
        return str(image_dict)
    except Exception as e:
        logger.info(f"generate_images exception: {str(e)}")
        return str(image_dict)


def parse_video_info(summary_data: str) -> dict:
    videos_prompt_info = VIDEO_DESC_PROMPT.format(summary_data)
    logger.info(
        f"\n====================================videos_prompt_info=\n{videos_prompt_info}"
    )

    video_info = query_from_openai_proxy(videos_prompt_info)
    logger.info(f"\n====================================video_info=\n {video_info}")

    # Extract the content within the ImagePrompt tag
    start_index = video_info.index("<VideoPrompt>") + 13
    end_index = video_info.index("</VideoPrompt>")
    content = video_info[start_index:end_index]
    logger.info(
        f"\n=====================================extract json prompt from video_info=\n{content}"
    )

    data_dict = json.loads(content)
    converted_dict = {key.replace(" ", "_"): value for key, value in data_dict.items()}
    return converted_dict


def generate_videos(converted_dict: dict) -> str:
    video_dict = []
    try:
        if len(converted_dict) == 0:
            return "No Videos"
        index = 0
        logger.info(
            f"parse_video_info: start generate videos, total: {len(converted_dict)}, current: {index}"
        )
        # start request text2video:
        for video_name, video_prompt in converted_dict.items():
            index += 1
            t2v_prompt = T2VPrompt()
            t2v_prompt.prompt = video_prompt
            download_url = t2v_request(t2v_prompt)
            if download_url is None:
                continue

            video_dict.append({"video_name": video_name, "url": download_url})
            logger.info(
                f"parse_video_info: generating videos, total: {len(converted_dict)}, completed: {index}, video_dict={str(video_dict)}"
            )
        return str(video_dict)
    except Exception as e:
        logger.info(f"generate_videos exception: {str(e)}")
        return str(video_dict)


def write_markdown_content(content, filename, filepath):
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    full_path = filepath + "/" + filename + ".md"

    with open(full_path, "w") as file:
        file.write(content)
    return full_path


def write_markdown_content_v2(content, filename, filepath):
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    full_path = filepath + "/" + filename + ".md"

    with open(full_path, "w") as file:
        file.write(content)
    return f"{DOWNLOAD_FOLDER}/{filename}.md"


def startup(idea: str):
    """
    split tasks from LLM (search from #param1 and get data, embedding and do #param2 actions, send message)

    example: Room-Temperature Superconductivity
    1. search from google (default), get top10 url and extract those texts from html.
    2. embedding those content
    3. do summary(default)
    4. generate image from stable diffusion
    5. prompt and generate markdown file.
    5. send to twitter/zhihu/Others.

    :param idea:
    :return: markdown file about the operation method of your idea.
    """
    operation_name = f"operation_doc_{str(int(time.time()))}"

    relative_data = search_relative_data_from_ds(idea)
    logger.info(f"relative_data:\n{relative_data}")

    embedding_client = embedding_knowledge(relative_data, operation_name)
    ans = embedding_client.similar_search(idea, 5)
    msgs = [a.page_content for a in ans]

    summary_data = "\n".join(msgs)
    logger.info(f"\nsummary_data=\n{summary_data}")

    image_prompt_dict = parse_image_info(summary_data)
    logger.info(f"\ncompleted parse_image_info=\n{image_prompt_dict}")

    image_data = generate_images(image_prompt_dict)
    logger.info(f"\ncompleted generate_images=\n{image_data}")

    # if exist Text2Video model, add video info
    video_prompt_dict = parse_video_info(summary_data)
    logger.info(f"\ncompleted parse_video_info=\n{video_prompt_dict}")

    video_data = generate_videos(video_prompt_dict)
    logger.info(f"\ncompleted generate_videos=\n{video_data}")

    prompt_req = OPERATE_PROMPT.format(summary_data, image_data, video_data)
    logger.info(f"\ngenerated markdown content prompt request=\n{prompt_req}")

    result = query_from_openai_proxy(prompt_req)
    logger.info(f"\ngenerated markdown content: \n{result}")

    # If deployed in PROD, use write_markdown_content_v2 instead.
    download_url = write_markdown_content_v2(
        result, operation_name, GENERATED_OPERATE_DATA_DEFAULT_DIR
    )

    logger.info(f"\nwrite file completed, download_url={download_url}")
    return download_url


def generate_md_file(idea) -> str:
    download_url = startup(idea)
    return download_url
