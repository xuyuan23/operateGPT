import os

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(ROOT_PATH, "models")


def get_device() -> str:
    import torch

    return (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )


LLM_MODEL_CONFIG = {
    "vicuna-13b": os.path.join(MODEL_PATH, "vicuna-13b"),
    "vicuna-7b": os.path.join(MODEL_PATH, "vicuna-7b"),
    "vicuna-13b-v1.5": os.path.join(MODEL_PATH, "vicuna-13b-v1.5"),
    "vicuna-7b-v1.5": os.path.join(MODEL_PATH, "vicuna-7b-v1.5"),
    "chatglm-6b": os.path.join(MODEL_PATH, "chatglm-6b"),
    "chatglm2-6b": os.path.join(MODEL_PATH, "chatglm2-6b"),
    "proxyllm": "chatgpt_proxyllm",
    "chatgpt_proxyllm": "chatgpt_proxyllm",
    "bard_proxyllm": "bard_proxyllm",
    "llama-2-7b": os.path.join(MODEL_PATH, "Llama-2-7b-chat-hf"),
    "llama-2-13b": os.path.join(MODEL_PATH, "Llama-2-13b-chat-hf"),
    "llama-2-70b": os.path.join(MODEL_PATH, "Llama-2-70b-chat-hf"),
    "baichuan-13b": os.path.join(MODEL_PATH, "Baichuan-13B-Chat"),
    "baichuan-7b": os.path.join(MODEL_PATH, "baichuan-7b"),
    "baichuan2-7b": os.path.join(MODEL_PATH, "Baichuan2-7B-Chat"),
    "baichuan2-13b": os.path.join(MODEL_PATH, "Baichuan2-13B-Chat"),
}

EMBEDDING_MODEL_CONFIG = {
    "text2vec": os.path.join(MODEL_PATH, "text2vec-large-chinese"),
    "text2vec-base": os.path.join(MODEL_PATH, "text2vec-base-chinese"),
    "m3e-base": os.path.join(MODEL_PATH, "m3e-base"),
    "m3e-large": os.path.join(MODEL_PATH, "m3e-large"),
    "bge-large-en": os.path.join(MODEL_PATH, "bge-large-en"),
    "bge-base-en": os.path.join(MODEL_PATH, "bge-base-en"),
    "bge-large-zh": os.path.join(MODEL_PATH, "bge-large-zh"),
    "bge-base-zh": os.path.join(MODEL_PATH, "bge-base-zh"),
    "sentence-transforms": os.path.join(MODEL_PATH, "all-MiniLM-L6-v2"),
}

ISDEBUG = False

VECTOR_SEARCH_TOP_K = 10
VS_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vs_store")
KNOWLEDGE_UPLOAD_ROOT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data"
)
KNOWLEDGE_CHUNK_SPLIT_SIZE = 100
