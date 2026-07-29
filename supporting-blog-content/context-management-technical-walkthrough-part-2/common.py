"""Shared helpers for the context management technical walkthrough index scripts.

Both `index_beir_datasets.py` and `index_browsecomp.py` connect the same way and
follow the same create-and-populate flow; that logic lives here.
"""

import os
from getpass import getpass

from elasticsearch import Elasticsearch, helpers


def get_client():
    """Connect to Elasticsearch using ES_URL / ES_API_KEY, or interactive prompts."""
    es_url = os.environ.get("ES_URL") or input(
        "Elasticsearch endpoint URL: "
    ).strip().rstrip("/")
    api_key = os.environ.get("ES_API_KEY") or getpass("Elastic API key: ")
    client = Elasticsearch(hosts=[es_url], api_key=api_key)
    print(client.info())
    return client


def populate_index(client, index_name, mappings, actions, *, skip_if_populated=False):
    """Create `index_name` with `mappings` and bulk-load `actions` into it.

    Deletes and recreates the index first, then reports the resulting doc count.
    If `skip_if_populated` is True and the index already holds documents, indexing
    is skipped and the existing index is reused. `actions` should be a lazy
    generator so nothing is streamed when indexing is skipped.
    """
    if skip_if_populated and client.indices.exists(index=index_name):
        count = client.count(index=index_name)["count"]
        if count > 0:
            print(
                f"Index '{index_name}' already has {count} documents — reusing it (skipping indexing)."
            )
            return

    client.indices.delete(index=index_name, ignore_unavailable=True)
    client.indices.create(index=index_name, mappings=mappings)
    helpers.bulk(client, actions)
    client.indices.refresh(index=index_name)
    print(
        f"Indexed {client.count(index=index_name)['count']} documents into '{index_name}'."
    )
