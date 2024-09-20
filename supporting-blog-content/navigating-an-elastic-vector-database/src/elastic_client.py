import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv(override=True)

ELASTIC_ENDPOINT_ID = os.environ.get("ELASTIC_ENDPOINT_ID")
ELASTIC_API_KEY = os.environ.get("ELASTIC_API_KEY")

es = Elasticsearch(
    hosts=ELASTIC_ENDPOINT_ID,
    api_key=ELASTIC_API_KEY,
)
