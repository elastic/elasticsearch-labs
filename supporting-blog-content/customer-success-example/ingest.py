from elasticsearch_serverless import Elasticsearch
import json
import os

client = Elasticsearch(
    os.getenv("ELASTICSEARCH_URL"), api_key=os.getenv("ES_API_KEY"), request_timeout=600
)

mappings = {
    "properties": {
        "semantic": {"type": "semantic_text", "inference_id": "e5-small"},
        "content": {"type": "text", "copy_to": "semantic"},
    }
}

# Create index
client.indices.create(index="search-faq", mappings=mappings)

inference_config = {
    "service": "elasticsearch",
    "service_settings": {
        "num_allocations": 1,
        "num_threads": 1,
        "model_id": ".multilingual-e5-small",
    },
}

# Create inference
client.inference.put(
    inference_id="e5-small",
    task_type="text_embedding",
    inference_config=inference_config,
)

with open("faq.json") as f:
    documents = json.load(f)


def generate_docs():
    index_name = "search-faq"
    for row in documents:
        yield {"index": {"_index": index_name}}
        yield row


# Index documents
client.bulk(operations=generate_docs())
