from operategpt.llms.llm_out.proxy.bard import bard_generate_stream
from operategpt.llms.llm_out.proxy.chatgpt import chatgpt_generate_stream
from operategpt.llms.llm_out.proxy.proxy_model import ProxyModel


def proxyllm_generate_stream(
    model: ProxyModel, tokenizer, params, device, context_len=2048
):
    generator_mapping = {
        "proxyllm": chatgpt_generate_stream,
        "chatgpt_proxyllm": chatgpt_generate_stream,
        "bard_proxyllm": bard_generate_stream,
    }
    model_params = model.get_params()
    model_name = model_params.model_name
    default_error_message = f"{model_name} LLM is not supported"
    generator_function = generator_mapping.get(
        model_name, lambda: default_error_message
    )

    yield from generator_function(model, tokenizer, params, device, context_len)
