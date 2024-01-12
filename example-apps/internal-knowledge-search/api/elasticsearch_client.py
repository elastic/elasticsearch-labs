from elasticsearch import Elasticsearch

import os

ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")


if ELASTICSEARCH_URL:
    if ELASTIC_API_KEY:
        elasticsearch_client = Elasticsearch(
            api_key=ELASTIC_API_KEY,
            hosts=[ELASTICSEARCH_URL],
        )
    elif ELASTIC_USERNAME and ELASTIC_PASSWORD:
        elasticsearch_client = Elasticsearch(
            basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
            hosts=[ELASTICSEARCH_URL],
        )
    else:
        raise ValueError(
            "Please provide either ELASTIC_API_KEY or ELASTIC_USERNAME and ELASTIC_PASSWORD"
        )
elif ELASTIC_CLOUD_ID:
    if ELASTIC_API_KEY:
        elasticsearch_client = Elasticsearch(
            cloud_id=ELASTIC_CLOUD_ID, api_key=ELASTIC_API_KEY
        )
    elif ELASTIC_USERNAME and ELASTIC_PASSWORD:
        elasticsearch_client = Elasticsearch(
            basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
            cloud_id=ELASTIC_CLOUD_ID
        )
    else:
        raise ValueError(
            "Please provide either ELASTIC_API_KEY or ELASTIC_USERNAME and ELASTIC_PASSWORD"
        )

else:
    raise ValueError(
        "Please provide either ELASTICSEARCH_URL or ELASTIC_CLOUD_ID and ELASTIC_API_KEY"
    )
