import json

import yaml
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer


def get_client_es():
    with open("../config.yml", "r") as file:
        config = yaml.safe_load(file)
    return Elasticsearch(cloud_id=config["cloud_id"], api_key=config["api_key"])


def get_text_vector(sentences):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(sentences)
    return embeddings


def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def chunk_data(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i : i + batch_size]


def generate_bulk_actions(index_name, data_batch):
    for item in data_batch:
        document_id = item["id"]
        item["description_embeddings"] = get_text_vector(item["description"])
        yield {"_index": index_name, "_id": document_id, "_source": item}


def index_data_in_batches(file_path, index_name, batch_size=100):
    data = read_json_file(file_path)

    for batch in chunk_data(data, batch_size):
        actions = generate_bulk_actions(index_name, batch)
        success, failed = helpers.bulk(get_client_es(), actions)
        print(f"Batch indexed: {success} successful, {failed} failed")


if __name__ == "__main__":
    index_data_in_batches(
        "../files/dataset/products.json", "products-catalog", batch_size=100
    )
