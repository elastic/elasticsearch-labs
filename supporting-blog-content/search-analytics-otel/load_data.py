#!/usr/bin/env python3
"""Load product data into Elasticsearch.

Usage:
    python load_data.py              # Load products (recreates index)
    python load_data.py --no-delete  # Load without deleting existing index
"""
import argparse
import json
import sys

from elasticsearch.helpers import bulk
from elastic_transport import ApiError, ConnectionError, ConnectionTimeout

from es_utils import (
    adapt_mapping_for_cluster,
    create_client,
    ensure_index,
    format_es_error,
    is_serverless,
    load_index_mapping,
    refresh_index_best_effort,
    require_search_config,
    verify_connection,
)


def main():
    parser = argparse.ArgumentParser(description="Load product data into Elasticsearch")
    parser.add_argument(
        "--no-delete", action="store_true", help="Don't delete existing index"
    )
    args = parser.parse_args()

    url, api_key, index = require_search_config()
    es = create_client(url, api_key)

    info = verify_connection(es)
    version = info.get("version", {}).get("number", "unknown")
    serverless = is_serverless(info)
    deployment = "Elastic Cloud Serverless" if serverless else "Elasticsearch"
    print(f"Connected to {deployment} {version}")

    mapping = adapt_mapping_for_cluster(load_index_mapping(), serverless)
    if serverless:
        print("Serverless detected — using mapping without shard/replica settings")

    ensure_index(es, index, mapping, no_delete=args.no_delete)

    try:
        with open("products.json", encoding="utf-8") as f:
            products = json.load(f)
    except FileNotFoundError:
        print("Error: products.json not found")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in products.json: {exc}")
        sys.exit(1)

    def actions():
        for product in products:
            yield {"_index": index, "_id": product["id"], "_source": product}

    try:
        success, errors = bulk(es, actions(), raise_on_error=False)
    except (ApiError, ConnectionError, ConnectionTimeout) as exc:
        print(f"Error: Bulk indexing failed: {format_es_error(exc)}")
        sys.exit(1)

    refresh_index_best_effort(es, index, serverless)

    if errors:
        print(f"Loaded {success} products with {len(errors)} errors:")
        for err in errors[:5]:
            print(f"  {err}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")
        sys.exit(1)

    print(f"Loaded {success} products into index '{index}' successfully")


if __name__ == "__main__":
    main()
