#!/usr/bin/env python3
"""Load product data into Elasticsearch.

Usage:
    python load_data.py              # Load products (recreates index)
    python load_data.py --no-delete  # Load without deleting existing index
"""
import json
import os
import sys
import argparse

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

load_dotenv(override=True)

ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_API_KEY = os.getenv("ELASTIC_API_KEY")
INDEX = os.getenv("SEARCH_INDEX", "products")


def main():
    parser = argparse.ArgumentParser(description="Load product data into Elasticsearch")
    parser.add_argument("--no-delete", action="store_true", help="Don't delete existing index")
    args = parser.parse_args()

    if not ES_URL or not ES_API_KEY:
        print("Error: Set ELASTICSEARCH_URL and ELASTIC_API_KEY in .env")
        sys.exit(1)

    es = Elasticsearch(hosts=[ES_URL], api_key=ES_API_KEY)

    # Verify connection
    info = es.info()
    print(f"Connected to Elasticsearch {info['version']['number']}")

    # Create index
    if es.indices.exists(index=INDEX):
        if args.no_delete:
            print(f"Index '{INDEX}' already exists (keeping existing data)")
        else:
            es.indices.delete(index=INDEX)
            print(f"Deleted existing index '{INDEX}'")

    if not es.indices.exists(index=INDEX):
        with open("index_mapping.json") as f:
            mapping = json.load(f)
        es.indices.create(index=INDEX, body=mapping)
        print(f"Created index '{INDEX}'")

    # Load products
    with open("products.json") as f:
        products = json.load(f)

    def actions():
        for product in products:
            yield {"_index": INDEX, "_id": product["id"], "_source": product}

    success, errors = bulk(es, actions(), raise_on_error=False)
    es.indices.refresh(index=INDEX)

    if errors:
        print(f"Loaded {success} products ({len(errors)} errors)")
        for err in errors[:5]:
            print(f"  Error: {err}")
    else:
        print(f"Loaded {success} products successfully")


if __name__ == "__main__":
    main()
