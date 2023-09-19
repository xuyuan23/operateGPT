from operategpt.llms.adapter import get_llm_model_adapter, BaseLLMAdaper, ModelType
from operategpt.llms.parameter import (
    ModelParameters,
    ProxyModelParameters,
)


class ModelLoader:
    def __init__(self, model_path: str, model_name: str = None) -> None:
        self.device = get_device()
        self.model_path = model_path
        self.model_name = model_name
        self.prompt_template: str = None

    def loader_with_params(self, model_params: ModelParameters):
        llm_adapter = get_llm_model_adapter(self.model_name, self.model_path)
        model_type = llm_adapter.model_type()
        self.prompt_template = model_params.prompt_template
        if model_type == ModelType.HF:
            return huggingface_loader(llm_adapter, model_params)
        elif model_type == ModelType.PROXY:
            return proxyllm_loader(model_params)
        else:
            raise Exception(f"Unkown model type {model_type}")


def get_device() -> str:
    import torch

    return (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )


def proxyllm_loader(model_params: ProxyModelParameters):
    from operategpt.llms.llm_out.proxy.proxy_model import ProxyModel

    model = ProxyModel(model_params)
    return model, model


def huggingface_loader(llm_adapter: BaseLLMAdaper, model_params: ModelParameters):
    import torch

    num_gpus = 0
    kwargs = {}
    device = model_params.device
    if device == "cpu":
        kwargs = {"torch_dtype": torch.float32}
    elif device == "cuda":
        kwargs = {"torch_dtype": torch.float16}
        num_gpus = torch.cuda.device_count()
        available_gpu_memory = get_gpu_memory(num_gpus)
        max_memory = {
            i: str(int(available_gpu_memory[i] * 0.85)) + "GiB" for i in range(num_gpus)
        }
        if num_gpus != 1:
            kwargs["device_map"] = "auto"
            if model_params.max_gpu_memory:
                max_memory = {i: model_params.max_gpu_memory for i in range(num_gpus)}
                kwargs["max_memory"] = max_memory
            else:
                kwargs["max_memory"] = max_memory

    model, tokenizer = llm_adapter.loader(model_params.model_path, kwargs)

    if (
        (device == "cuda" and num_gpus == 1 and not model_params.cpu_offloading)
        or device == "mps"
        and tokenizer
    ):
        try:
            model.to(device)
        except ValueError:
            pass
        except AttributeError:
            pass
    return model, tokenizer


def get_gpu_memory(max_gpus=None):
    import torch

    gpu_memory = []
    num_gpus = (
        torch.cuda.device_count()
        if max_gpus is None
        else min(max_gpus, torch.cuda.device_count())
    )

    for gpu_id in range(num_gpus):
        with torch.cuda.device(gpu_id):
            device = torch.cuda.current_device()
            gpu_properties = torch.cuda.get_device_properties(device)
            total_memory = gpu_properties.total_memory / (1024**3)
            allocated_memory = torch.cuda.memory_allocated() / (1024**3)
            available_memory = total_memory - allocated_memory
            gpu_memory.append(available_memory)
    return gpu_memory
