"""Create the BrowseComp-Plus document index and populate it with sample data.

Standalone extraction of the indexing step from the `index-facts-kis.ipynb`
notebook. Streams a small slice of the BrowseComp-Plus corpus into a single
BM25-only index, deriving a `title` from each document's front matter.

Connection is read from environment variables, falling back to an interactive
prompt:

    ES_URL            Elasticsearch endpoint URL
    ELASTIC_API_KEY   Elastic API key

Run:

    pip install -r requirements.txt
    python index_browsecomp.py
"""

import os
import re
from getpass import getpass

from datasets import load_dataset
from elasticsearch import Elasticsearch, helpers

INDEX_NAME = "browsecomp-plus"
SAMPLE_DOCS = 50  # documents to index (one KI is generated per doc, so keep it small)


def get_client():
    es_url = os.environ.get("ES_URL") or input("Elasticsearch endpoint URL: ").strip().rstrip("/")
    api_key = os.environ.get("ELASTIC_API_KEY") or getpass("Elastic API key: ")
    client = Elasticsearch(hosts=[es_url], api_key=api_key)
    print(client.info())
    return client


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


def actions(corpus, n):
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

    if (
        client.indices.exists(index=INDEX_NAME)
        and client.count(index=INDEX_NAME)["count"] > 0
    ):
        count = client.count(index=INDEX_NAME)["count"]
        print(
            f"Index '{INDEX_NAME}' already has {count} documents — reusing it (skipping indexing)."
        )
        return

    client.indices.delete(index=INDEX_NAME, ignore_unavailable=True)
    client.indices.create(
        index=INDEX_NAME,
        mappings={
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
                    "meta": {"description": "Document title (from the document's front matter)."},
                },
                "text": {
                    "type": "text",
                    "meta": {"description": "Full document text: title, date, and body content."},
                },
            },
        },
    )

    corpus = load_dataset(
        "Tevatron/browsecomp-plus-corpus", split="train", streaming=True
    )

    helpers.bulk(client, actions(corpus, SAMPLE_DOCS))
    client.indices.refresh(index=INDEX_NAME)
    print(
        f"Indexed {client.count(index=INDEX_NAME)['count']} documents into '{INDEX_NAME}'."
    )


if __name__ == "__main__":
    main()
