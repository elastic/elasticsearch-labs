"""Elasticsearch client and index name, read from .env (values in .env override the shell)."""

import os
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env", override=True)


def get_client() -> Elasticsearch:
    return Elasticsearch(
        os.environ["ES_URL"], api_key=os.environ["ES_API_KEY"], request_timeout=120
    )


def index_name() -> str:
    return os.environ.get("INDEX_NAME", "fingerprint-demo")


def create_index(es: Elasticsearch, name: str) -> None:
    """Create the index from mappings/index.json (replaces an existing one)."""
    import json

    es.indices.delete(index=name, ignore_unavailable=True)
    es.indices.create(
        index=name, **json.loads((HERE / "mappings/index.json").read_text())
    )
