"""Create the BrowseComp-Plus document index and populate it with sample data.

Streams a small slice of the BrowseComp-Plus corpus into an index enriched
with mapping metadata (`_meta.description` and per-field `meta.description`).
Derives a title from the beginning of the document.
May be used in conjunction with the context management technical walkthrough blog.

Connection is read from environment variables, falling back to an interactive
prompt:

    ES_URL            Elasticsearch endpoint URL
    ES_API_KEY   Elastic API key

Run:

    pip install -r requirements.txt
    python index_browsecomp.py
"""

import re

from datasets import load_dataset

from common import get_client, populate_index

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
            "meta": {"description": "Document title (from the document's front matter)."},
        },
        "text": {
            "type": "text",
            "meta": {"description": "Full document text: title, date, and body content."},
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
