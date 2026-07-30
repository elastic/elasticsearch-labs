"""Create the three BEIR index-selection indices and populate them with sample data.

Streams a small slice of three BEIR benchmark corpora (financial Q&A,
biomedical, scientific fact-checking) into three BM25-only indices, each enriched
with mapping metadata (`_meta.description` and per-field `meta.description`).
May be used in conjunction with the precomputed context technical walkthrough blog.

Connection is read from environment variables, falling back to an interactive
prompt:

    ES_URL            Elasticsearch endpoint URL
    ES_API_KEY   Elastic API key

Run:

    pip install -r requirements.txt
    python index_beir_datasets.py
"""

import os
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

SAMPLE_DOCS = 50

DATASETS = [
    {
        "hf_dataset": "BeIR/fiqa",
        "hf_config": "corpus",
        "hf_split": "corpus",
        "index_name": "beir-fiqa",
        "meta_description": (
            "FiQA: financial question answering corpus from StackExchange Finance "
            "community posts and web crawls. Covers investments, banking, taxes, "
            "and market analysis. BM25-only index."
        ),
    },
    {
        "hf_dataset": "BeIR/nfcorpus",
        "hf_config": "corpus",
        "hf_split": "corpus",
        "index_name": "beir-nfcorpus",
        "meta_description": (
            "NFCorpus: biomedical information retrieval corpus from NutritionFacts.org. "
            "Contains nutrition science and medical research documents on diet, disease, "
            "and health interventions. BM25-only index."
        ),
    },
    {
        "hf_dataset": "BeIR/scifact",
        "hf_config": "corpus",
        "hf_split": "corpus",
        "index_name": "beir-scifact",
        "meta_description": (
            "SciFact: scientific fact-checking corpus of biomedical research abstracts "
            "used to verify factual claims in peer-reviewed literature. BM25-only index."
        ),
    },
]

PROPERTIES = {
    "title": {
        "type": "text",
        "meta": {"description": "Document or article title."},
    },
    "text": {
        "type": "text",
        "meta": {"description": "Full document body text."},
    },
}


def actions(ds, n):
    corpus = load_dataset(
        ds["hf_dataset"], ds["hf_config"], split=ds["hf_split"], streaming=True
    )
    for i, row in enumerate(corpus):
        if i >= n:
            break
        yield {
            "_index": ds["index_name"],
            "_id": row["_id"],
            "_source": {
                "title": row.get("title", "").strip()
                or " ".join(row.get("text", "").split())[:100],
                "text": row.get("text", ""),
            },
        }


def main():
    client = get_client()

    for ds in DATASETS:
        mappings = {
            "_meta": {"description": ds["meta_description"]},
            "properties": PROPERTIES,
        }
        populate_index(client, ds["index_name"], mappings, actions(ds, SAMPLE_DOCS))


if __name__ == "__main__":
    main()
