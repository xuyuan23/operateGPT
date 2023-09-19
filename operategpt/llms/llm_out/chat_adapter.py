#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import cache
from typing import List, Dict, Tuple

from operategpt.llms.message.base_message import ModelMessage, ModelMessageRoleType
from operategpt.llms.message.conversation import Conversation, get_conv_template


class BaseChatAdpter:
    """The Base class for chat with llm models. it will match the model,
    and fetch output from model"""

    def match(self, model_path: str):
        return False

    def get_generate_stream_func(self, model_path: str):
        """Return the generate stream handler func"""
        from operategpt.llms.llm_out.inference import generate_stream

        return generate_stream

    def get_conv_template(self, model_path: str) -> Conversation:
        return None

    def model_adaptation(
        self, params: Dict, model_path: str, prompt_template: str = None
    ) -> Tuple[Dict, Dict]:
        """Params adaptation"""
        conv = self.get_conv_template(model_path)
        messages = params.get("messages")
        model_context = {"prompt_echo_len_char": -1}

        if messages:
            # Dict message to ModelMessage
            messages = [
                m if isinstance(m, ModelMessage) else ModelMessage(**m)
                for m in messages
            ]
            params["messages"] = messages

        if prompt_template:
            print(f"Use prompt template {prompt_template} from config")
            conv = get_conv_template(prompt_template)

        if not conv or not messages:
            # Nothing to do
            print(
                f"No conv from model_path {model_path} or no messages in params, {self}"
            )
            return params, model_context
        conv = conv.copy()
        system_messages = []
        for message in messages:
            role, content = None, None
            if isinstance(message, ModelMessage):
                role = message.role
                content = message.content
            elif isinstance(message, dict):
                role = message["role"]
                content = message["content"]
            else:
                raise ValueError(f"Invalid message type: {message}")

            if role == ModelMessageRoleType.SYSTEM:
                # Support for multiple system messages
                system_messages.append(content)
            elif role == ModelMessageRoleType.HUMAN:
                conv.append_message(conv.roles[0], content)
            elif role == ModelMessageRoleType.AI:
                conv.append_message(conv.roles[1], content)
            else:
                raise ValueError(f"Unknown role: {role}")
        if system_messages:
            conv.update_system_message("".join(system_messages))
        # Add a blank message for the assistant.
        conv.append_message(conv.roles[1], None)
        new_prompt = conv.get_prompt()
        # Overwrite the original prompt
        # TODO remote bos token and eos token from tokenizer_config.json of model
        prompt_echo_len_char = len(new_prompt.replace("</s>", "").replace("<s>", ""))
        model_context["prompt_echo_len_char"] = prompt_echo_len_char
        model_context["echo"] = params.get("echo", True)
        params["prompt"] = new_prompt

        # Overwrite model params:
        params["stop"] = conv.stop_str

        return params, model_context


llm_model_chat_adapters: List[BaseChatAdpter] = []


def register_llm_model_chat_adapter(cls):
    """Register a chat adapter"""
    llm_model_chat_adapters.append(cls())


@cache
def get_llm_chat_adapter(model_name: str, model_path: str) -> BaseChatAdpter:
    """Get a chat generate func for a model"""
    for adapter in llm_model_chat_adapters:
        if adapter.match(model_name):
            print(f"Get model chat adapter with model name {model_name}, {adapter}")
            return adapter
    for adapter in llm_model_chat_adapters:
        if adapter.match(model_path):
            print(f"Get model chat adapter with model path {model_path}, {adapter}")
            return adapter
    raise ValueError(
        f"Invalid model for chat adapter with model name {model_name} and model path {model_path}"
    )


class VicunaChatAdapter(BaseChatAdpter):
    """Model chat Adapter for vicuna"""

    def _is_llama2_based(self, model_path: str):
        # see https://huggingface.co/lmsys/vicuna-13b-v1.5
        return "v1.5" in model_path.lower()

    def match(self, model_path: str):
        return "vicuna" in model_path.lower()

    def get_conv_template(self, model_path: str) -> Conversation:
        if self._is_llama2_based(model_path):
            return get_conv_template("vicuna_v1.1")
        return None

    def get_generate_stream_func(self, model_path: str):
        from operategpt.llms.llm_out.vicuna_base_llm import generate_stream

        if self._is_llama2_based(model_path):
            return super().get_generate_stream_func(model_path)
        return generate_stream


class ChatGLMChatAdapter(BaseChatAdpter):
    """Model chat Adapter for ChatGLM"""

    def match(self, model_path: str):
        return "chatglm" in model_path

    def get_generate_stream_func(self, model_path: str):
        from operategpt.llms.llm_out.chatglm_llm import chatglm_generate_stream

        return chatglm_generate_stream


class ProxyllmChatAdapter(BaseChatAdpter):
    def match(self, model_path: str):
        return "proxyllm" in model_path

    def get_generate_stream_func(self, model_path: str):
        from operategpt.llms.llm_out.proxy_llm import proxyllm_generate_stream

        return proxyllm_generate_stream


class BaichuanChatAdapter(BaseChatAdpter):
    def match(self, model_path: str):
        return "baichuan" in model_path.lower()

    def get_conv_template(self, model_path: str) -> Conversation:
        if "chat" in model_path.lower():
            return get_conv_template("baichuan-chat")
        return get_conv_template("zero_shot")


register_llm_model_chat_adapter(VicunaChatAdapter)
register_llm_model_chat_adapter(ChatGLMChatAdapter)
register_llm_model_chat_adapter(BaichuanChatAdapter)
register_llm_model_chat_adapter(ProxyllmChatAdapter)
register_llm_model_chat_adapter(BaseChatAdpter)
