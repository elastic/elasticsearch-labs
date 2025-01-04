import os

import vertexai
from langchain_aws import ChatBedrock
from langchain_cohere import ChatCohere
from langchain_google_vertexai import ChatVertexAI
from langchain_mistralai import ChatMistralAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI

LLM_TYPE = os.getenv("LLM_TYPE", "openai")


def init_openai_chat(temperature):
    # Include streaming usage as this allows recording of LLM metrics
    return ChatOpenAI(
        model=os.getenv("CHAT_MODEL"),
        streaming=True,
        temperature=temperature,
        model_kwargs={"stream_options": {"include_usage": True}},
    )


def init_vertex_chat(temperature):
    return ChatVertexAI(
        model_name=os.getenv("CHAT_MODEL"), streaming=True, temperature=temperature
    )


def init_azure_chat(temperature):
    # Include streaming usage as this allows recording of LLM metrics
    return AzureChatOpenAI(
        model=os.getenv("CHAT_DEPLOYMENT"),
        streaming=True,
        temperature=temperature,
        model_kwargs={"stream_options": {"include_usage": True}},
    )


def init_bedrock(temperature):
    return ChatBedrock(
        model_id=os.getenv("CHAT_MODEL"),
        streaming=True,
        model_kwargs={"temperature": temperature},
    )


def init_mistral_chat(temperature):
    return ChatMistralAI(
        model=os.getenv("CHAT_MODEL"), streaming=True, temperature=temperature
    )


def init_cohere_chat(temperature):
    return ChatCohere(model=os.getenv("CHAT_MODEL"), temperature=temperature)


MAP_LLM_TYPE_TO_CHAT_MODEL = {
    "azure": init_azure_chat,
    "bedrock": init_bedrock,
    "openai": init_openai_chat,
    "vertex": init_vertex_chat,
    "mistral": init_mistral_chat,
    "cohere": init_cohere_chat,
}


def get_llm(temperature=0):
    if LLM_TYPE not in MAP_LLM_TYPE_TO_CHAT_MODEL:
        raise Exception(
            "LLM type not found. Please set LLM_TYPE to one of: "
            + ", ".join(MAP_LLM_TYPE_TO_CHAT_MODEL.keys())
            + "."
        )

    return MAP_LLM_TYPE_TO_CHAT_MODEL[LLM_TYPE](temperature=temperature)
