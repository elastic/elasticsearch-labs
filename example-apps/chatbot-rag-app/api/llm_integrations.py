from langchain_openai import AzureChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain_cohere import ChatCohere
from langchain_mistralai import ChatMistralAI
from langchain_aws import ChatBedrock

import os
import vertexai

LLM_TYPE = os.getenv("LLM_TYPE", "openai")


def init_openai_chat(temperature):
    return ChatOpenAI(
        model=os.getenv("CHAT_MODEL"), streaming=True, temperature=temperature
    )


def init_vertex_chat(temperature):
    VERTEX_PROJECT_ID = os.getenv("VERTEX_PROJECT_ID")
    VERTEX_REGION = os.getenv("VERTEX_REGION", "us-central1")
    vertexai.init(project=VERTEX_PROJECT_ID, location=VERTEX_REGION)
    return ChatVertexAI(streaming=True, temperature=temperature)


def init_azure_chat(temperature):
    return AzureChatOpenAI(
        model=os.getenv("CHAT_DEPLOYMENT"), streaming=True, temperature=temperature
    )


def init_bedrock(temperature):
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_MODEL_ID = os.getenv("AWS_MODEL_ID", "anthropic.claude-v2")
    return ChatBedrock(
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        model_id=AWS_MODEL_ID,
        streaming=True,
        model_kwargs={"temperature": temperature},
    )


def init_mistral_chat(temperature):
    MISTRAL_API_ENDPOINT = os.getenv("MISTRAL_API_ENDPOINT")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "Mistral-large")
    kwargs = {
        "mistral_api_key": MISTRAL_API_KEY,
        "temperature": temperature,
    }
    if MISTRAL_API_ENDPOINT:
        kwargs["endpoint"] = MISTRAL_API_ENDPOINT
    if MISTRAL_MODEL:
        kwargs["model"] = MISTRAL_MODEL
    return ChatMistralAI(**kwargs)


def init_cohere_chat(temperature):
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    COHERE_MODEL = os.getenv("COHERE_MODEL")
    return ChatCohere(
        cohere_api_key=COHERE_API_KEY, model=COHERE_MODEL, temperature=temperature
    )


MAP_LLM_TYPE_TO_CHAT_MODEL = {
    "azure": init_azure_chat,
    "bedrock": init_bedrock,
    "openai": init_openai_chat,
    "vertex": init_vertex_chat,
    "mistral": init_mistral_chat,
    "cohere": init_cohere_chat,
}


def get_llm(temperature=0):
    if not LLM_TYPE in MAP_LLM_TYPE_TO_CHAT_MODEL:
        raise Exception(
            "LLM type not found. Please set LLM_TYPE to one of: "
            + ", ".join(MAP_LLM_TYPE_TO_CHAT_MODEL.keys())
            + "."
        )

    return MAP_LLM_TYPE_TO_CHAT_MODEL[LLM_TYPE](temperature=temperature)
