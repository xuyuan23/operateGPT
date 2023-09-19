from dataclasses import dataclass, field
from typing import Optional

from operategpt.llms.parameter_util import BaseParameters


@dataclass
class BaseModelParameters(BaseParameters):
    model_name: str = field(metadata={"help": "Model name", "tags": "fixed"})
    model_path: str = field(metadata={"help": "Model path", "tags": "fixed"})


@dataclass
class ModelParameters(BaseModelParameters):
    device: Optional[str] = field(
        default=None,
        metadata={
            "help": "Device to run model. If None, the device is automatically determined"
        },
    )
    model_type: Optional[str] = field(
        default="huggingface",
        metadata={
            "help": "Model type, huggingface, llama.cpp and proxy",
            "tags": "fixed",
        },
    )
    prompt_template: Optional[str] = field(
        default=None,
        metadata={
            "help": f"Prompt template. If None, the prompt template is automatically determined from model path, supported template: []"
        },
    )
    max_context_size: Optional[int] = field(
        default=4096, metadata={"help": "Maximum context size"}
    )

    num_gpus: Optional[int] = field(
        default=None,
        metadata={
            "help": "The number of gpus you expect to use, if it is empty, use all of them as much as possible"
        },
    )
    max_gpu_memory: Optional[str] = field(
        default=None,
        metadata={
            "help": "The maximum memory limit of each GPU, only valid in multi-GPU configuration"
        },
    )
    cpu_offloading: Optional[bool] = field(
        default=False, metadata={"help": "CPU offloading"}
    )
    load_8bit: Optional[bool] = field(
        default=False, metadata={"help": "8-bit quantization"}
    )
    load_4bit: Optional[bool] = field(
        default=False, metadata={"help": "4-bit quantization"}
    )
    quant_type: Optional[str] = field(
        default="nf4",
        metadata={
            "valid_values": ["nf4", "fp4"],
            "help": "Quantization datatypes, `fp4` (four bit float) and `nf4` (normal four bit float), only valid when load_4bit=True",
        },
    )
    use_double_quant: Optional[bool] = field(
        default=True,
        metadata={"help": "Nested quantization, only valid when load_4bit=True"},
    )
    compute_dtype: Optional[str] = field(
        default=None,
        metadata={
            "valid_values": ["bfloat16", "float16", "float32"],
            "help": "Model compute type",
        },
    )
    trust_remote_code: Optional[bool] = field(
        default=True, metadata={"help": "Trust remote code"}
    )
    verbose: Optional[bool] = field(
        default=False, metadata={"help": "Show verbose output."}
    )


@dataclass
class ProxyModelParameters(BaseModelParameters):
    proxy_server_url: str = field(
        metadata={
            "help": "Proxy server url, such as: https://api.openai.com/v1/chat/completions"
        },
    )
    proxy_api_key: str = field(
        metadata={"tags": "privacy", "help": "The api key of current proxy LLM"},
    )
    proxyllm_backend: Optional[str] = field(
        default=None,
        metadata={
            "help": "The model name actually pass to current proxy server url, such as gpt-3.5-turbo, gpt-4, chatglm_pro, chatglm_std and so on"
        },
    )
    model_type: Optional[str] = field(
        default="proxy",
        metadata={
            "help": "Model type, huggingface, llama.cpp and proxy",
            "tags": "fixed",
        },
    )
    device: Optional[str] = field(
        default=None,
        metadata={
            "help": "Device to run model. If None, the device is automatically determined"
        },
    )
    prompt_template: Optional[str] = field(
        default=None,
        metadata={
            "help": f"Prompt template. If None, the prompt template is automatically determined from model path, supported template: []"
        },
    )
    max_context_size: Optional[int] = field(
        default=4096, metadata={"help": "Maximum context size"}
    )


@dataclass
class LlamaCppModelParameters(ModelParameters):
    seed: Optional[int] = field(
        default=-1, metadata={"help": "Random seed for llama-cpp models. -1 for random"}
    )
    n_threads: Optional[int] = field(
        default=None,
        metadata={
            "help": "Number of threads to use. If None, the number of threads is automatically determined"
        },
    )
    n_batch: Optional[int] = field(
        default=512,
        metadata={
            "help": "Maximum number of prompt tokens to batch together when calling llama_eval"
        },
    )
    n_gpu_layers: Optional[int] = field(
        default=1000000000,
        metadata={
            "help": "Number of layers to offload to the GPU, Set this to 1000000000 to offload all layers to the GPU."
        },
    )
    n_gqa: Optional[int] = field(
        default=None,
        metadata={"help": "Grouped-query attention. Must be 8 for llama-2 70b."},
    )
    rms_norm_eps: Optional[float] = field(
        default=5e-06, metadata={"help": "5e-6 is a good value for llama-2 models."}
    )
    cache_capacity: Optional[str] = field(
        default=None,
        metadata={
            "help": "Maximum cache capacity. Examples: 2000MiB, 2GiB. When provided without units, bytes will be assumed. "
        },
    )
    prefer_cpu: Optional[bool] = field(
        default=False,
        metadata={
            "help": "If a GPU is available, it will be preferred by default, unless prefer_cpu=False is configured."
        },
    )
