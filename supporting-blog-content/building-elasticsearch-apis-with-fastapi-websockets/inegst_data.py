import json
import os

from elasticsearch import Elasticsearch

es_client = Elasticsearch(
    hosts=[os.environ["ELASTICSEARCH_ENDPOINT"]],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

PRODUCTS_INDEX = "products"


def create_products_index():
    try:
        mapping = {
            "mappings": {
                "properties": {
                    "product_name": {"type": "text", "analyzer": "standard"},
                    "price": {"type": "float"},
                    "description": {"type": "text", "analyzer": "standard"},
                }
            }
        }

        es_client.indices.create(index=PRODUCTS_INDEX, body=mapping)
        print(f"Index {PRODUCTS_INDEX} created successfully")
    except Exception as e:
        print(f"Error creating index: {e}")


def load_products_from_ndjson():
    try:
        if not os.path.exists("products.ndjson"):
            print("Error: products.ndjson file not found!")
            return

        products_loaded = 0
        with open("products.ndjson", "r") as f:
            for line in f:
                if line.strip():
                    product_data = json.loads(line.strip())
                    es_client.index(index=PRODUCTS_INDEX, body=product_data)
                    products_loaded += 1

        print(f"Successfully loaded {products_loaded} products into Elasticsearch")

    except Exception as e:
        print(f"Error loading products: {e}")


if __name__ == "__main__":
    create_products_index()
    load_products_from_ndjson()
