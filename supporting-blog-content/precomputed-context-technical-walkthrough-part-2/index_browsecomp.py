"""Create the BrowseComp-Plus document index and populate it with sample data.

Streams a small slice of the BrowseComp-Plus corpus into an index enriched
with mapping metadata (`_meta.description` and per-field `meta.description`).
Derives a title from the beginning of the document.
May be used in conjunction with the precomputed context technical walkthrough blog.

Connection is read from environment variables, falling back to an interactive
prompt:

    ES_URL            Elasticsearch endpoint URL
    ES_API_KEY   Elastic API key

Run:

    pip install -r requirements.txt
    python index_browsecomp.py
"""

import os
import re
from getpass import getpass

from datasets import load_dataset
from elasticsearch import Elasticsearch, helpers


def get_client():
    es_url = os.environ.get("ES_URL") or input(
        "Elasticsearch endpoint URL: "
    ).strip().rstrip("/")
    api_key = os.environ.get("ES_API_KEY") or getpass("Elastic API key: ")
    client = Elasticsearch(hosts=[es_url], api_key=api_key)
    print(client.info())
    return client


def populate_index(client, index_name, mappings, actions, *, skip_if_populated=False):
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

INDEX_NAME = "browsecomp-plus"
SAMPLE_DOCS = 50  # documents to index (one KI is generated per doc, so keep it small)

MAPPINGS = {
    "_meta": {
        "description": (
            "BrowseComp-Plus corpus: ~100k human-verified web documents "
            "(news articles, Wikipedia entries, institutional pages) used as a "
            "reasoning-intensive browsing/QA retrieval benchmark. BM25-only index."
        )
    },
    "properties": {
        "docid": {
            "type": "keyword",
            "meta": {"description": "Stable corpus document id."},
        },
        "url": {
            "type": "keyword",
            "meta": {"description": "Source URL the document was crawled from."},
        },
        "title": {
            "type": "text",
            "meta": {
                "description": "Document title (from the document's front matter)."
            },
        },
        "text": {
            "type": "text",
            "meta": {
                "description": "Full document text: title, date, and body content."
            },
        },
    },
}


def extract_title(text):
    # Each BrowseComp-Plus doc opens with a YAML front-matter block (--- ... ---)
    # whose `title:` field holds the real title; the first body line is just the
    # "---" delimiter. Read the title from there, else fall back to the first real line.
    m = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
    if m:
        return m.group(1).strip()[:200]
    for line in text.splitlines():
        s = line.strip()
        if s and s != "---":
            return s[:200]
    return ""


def actions(n):
    corpus = load_dataset(
        "Tevatron/browsecomp-plus-corpus", split="train", streaming=True
    )
    for i, row in enumerate(corpus):
        if i >= n:
            break
        text = row["text"]
        yield {
            "_index": INDEX_NAME,
            "_id": row["docid"],
            "_source": {
                "docid": row["docid"],
                "url": row["url"],
                "title": extract_title(text),
                "text": text,
            },
        }


def main():
    client = get_client()
    populate_index(
        client, INDEX_NAME, MAPPINGS, actions(SAMPLE_DOCS), skip_if_populated=True
    )


if __name__ == "__main__":
    main()
