import os

from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchChatMessageHistory

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")

if ELASTICSEARCH_USER:
    elasticsearch_client = Elasticsearch(
        hosts=[ELASTICSEARCH_URL],
        basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
    )
elif ELASTICSEARCH_API_KEY:
    elasticsearch_client = Elasticsearch(
        hosts=[ELASTICSEARCH_URL], api_key=ELASTICSEARCH_API_KEY
    )
else:
    raise ValueError(
        "Please provide either ELASTICSEARCH_USER or ELASTICSEARCH_API_KEY"
    )


def get_elasticsearch_chat_message_history(index, session_id):
    return ElasticsearchChatMessageHistory(
        es_connection=elasticsearch_client, index=index, session_id=session_id
    )
