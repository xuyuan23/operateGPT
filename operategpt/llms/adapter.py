from functools import cache
from typing import List

from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel

from operategpt.llms.model_config import get_device
from operategpt.llms.parameter import ModelParameters


class ModelType:
    """ "Type of model"""

    HF = "huggingface"
    LLAMA_CPP = "llama.cpp"
    PROXY = "proxy"


class BaseLLMAdaper:
    """The Base class for multiply model, in our project.
    We will support those model, which performance resemble ChatGPT"""

    def use_fast_tokenizer(self) -> bool:
        return False

    def model_type(self) -> str:
        return ModelType.HF

    def model_param_class(self, model_type: str = None) -> ModelParameters:
        return ModelParameters

    def match(self, model_path: str):
        return False

    def loader(self, model_path: str, from_pretrained_kwargs: dict):
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
        model = AutoModelForCausalLM.from_pretrained(
            model_path, low_cpu_mem_usage=True, **from_pretrained_kwargs
        )
        return model, tokenizer


llm_model_adapters: List[BaseLLMAdaper] = []


# Register llm models to adapters, by this we can use multi models.
def register_llm_model_adapters(cls):
    """Register a llm model adapter."""
    llm_model_adapters.append(cls())


@cache
def get_llm_model_adapter(model_name: str, model_path: str) -> BaseLLMAdaper:
    # Prefer using model name matching
    for adapter in llm_model_adapters:
        if adapter.match(model_name):
            return adapter

    for adapter in llm_model_adapters:
        if model_path and adapter.match(model_path):
            return adapter

    raise ValueError(
        f"Invalid model adapter for model name {model_name} and model path {model_path}"
    )


def _parse_model_param_class(model_name: str, model_path: str) -> ModelParameters:
    try:
        llm_adapter = get_llm_model_adapter(model_name, model_path)
        return llm_adapter.model_param_class()
    except Exception as e:
        print(f"_parse_model_param_class error: {str(e)}")
        return ModelParameters


# TODO support cpu? for practise we support gpt4all or chatglm-6b-int4?


class VicunaLLMAdapater(BaseLLMAdaper):
    """Vicuna Adapter"""

    def match(self, model_path: str):
        return "vicuna" in model_path

    def loader(self, model_path: str, from_pretrained_kwagrs: dict):
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
        model = AutoModelForCausalLM.from_pretrained(
            model_path, low_cpu_mem_usage=True, **from_pretrained_kwagrs
        )
        return model, tokenizer


def auto_configure_device_map(num_gpus):
    """handling multi gpu calls"""
    # transformer.word_embeddings occupying 1 floors
    # transformer.final_layernorm and lm_head occupying 1 floors
    # transformer.layers occupying 28 floors
    # Allocate a total of 30 layers to number On gpus cards
    num_trans_layers = 28
    per_gpu_layers = 30 / num_gpus
    # Bugfix: call torch.embedding in Linux and the incoming weight and input are not on the same device, resulting in a RuntimeError
    # Under Windows, model. device will be set to transformer. word_ Embeddings. device
    # Under Linux, model. device will be set to lm_ Head.device
    # When calling chat or stream_ During chat, input_ IDS will be placed on model. device
    # If transformer. word_ If embeddings. device and model. device are different, it will cause a RuntimeError
    # Therefore, here we will transform. word_ Embeddings, transformer. final_ Layernorm, lm_ Put all the heads on the first card
    device_map = {
        "transformer.embedding.word_embeddings": 0,
        "transformer.encoder.final_layernorm": 0,
        "transformer.output_layer": 0,
        "transformer.rotary_pos_emb": 0,
        "lm_head": 0,
    }

    used = 2
    gpu_target = 0
    for i in range(num_trans_layers):
        if used >= per_gpu_layers:
            gpu_target += 1
            used = 0
        assert gpu_target < num_gpus
        device_map[f"transformer.encoder.layers.{i}"] = gpu_target
        used += 1

    return device_map


class ChatGLMAdapater(BaseLLMAdaper):
    """LLM Adatpter for THUDM/chatglm-6b"""

    def match(self, model_path: str):
        return "chatglm" in model_path

    def loader(self, model_path: str, from_pretrained_kwargs: dict):
        import torch

        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        if get_device() != "cuda":
            model = AutoModel.from_pretrained(
                model_path, trust_remote_code=True, **from_pretrained_kwargs
            ).float()
            return model, tokenizer
        else:
            device_map = None
            num_gpus = torch.cuda.device_count()
            model = (
                AutoModel.from_pretrained(
                    model_path, trust_remote_code=True, **from_pretrained_kwargs
                ).half()
                # .cuda()
            )
            from accelerate import dispatch_model

            if device_map is None:
                device_map = auto_configure_device_map(num_gpus)

            model = dispatch_model(model, device_map=device_map)

            return model, tokenizer


class ProxyllmAdapter(BaseLLMAdaper):
    """The model adapter for local proxy"""

    def model_type(self) -> str:
        return ModelType.PROXY

    def match(self, model_path: str):
        return "proxyllm" in model_path

    def loader(self, model_path: str, from_pretrained_kwargs: dict):
        return "proxyllm", None


class Llama2Adapter(BaseLLMAdaper):
    """The model adapter for llama-2"""

    def match(self, model_path: str):
        return "llama-2" in model_path.lower()

    def loader(self, model_path: str, from_pretrained_kwargs: dict):
        model, tokenizer = super().loader(model_path, from_pretrained_kwargs)
        model.config.eos_token_id = tokenizer.eos_token_id
        model.config.pad_token_id = tokenizer.pad_token_id
        return model, tokenizer


class BaichuanAdapter(BaseLLMAdaper):
    """The model adapter for Baichuan models (e.g., baichuan-inc/Baichuan-13B-Chat)"""

    def match(self, model_path: str):
        return "baichuan" in model_path.lower()

    def loader(self, model_path: str, from_pretrained_kwargs: dict):
        tokenizer = AutoTokenizer.from_pretrained(
            model_path, trust_remote_code=True, use_fast=False
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            **from_pretrained_kwargs,
        )
        return model, tokenizer


register_llm_model_adapters(VicunaLLMAdapater)
register_llm_model_adapters(ChatGLMAdapater)
register_llm_model_adapters(Llama2Adapter)
register_llm_model_adapters(BaichuanAdapter)

register_llm_model_adapters(ProxyllmAdapter)
register_llm_model_adapters(BaseLLMAdaper)
