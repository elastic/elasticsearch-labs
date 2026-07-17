# Context management technical walkthrough — index setup scripts

Standalone scripts that create and populate the four sample indices used in the
[Context Engine manual-walkthrough notebooks](../../notebooks/context-engine/manual-walkthrough).
They extract only the index-creation and sample-data steps so you can stand up
the data without running the notebooks.

All four indices are BM25-only and are enriched with mapping metadata
(`_meta.description` and per-field `meta.description`).

| Script | Indices | Dataset |
|--------|---------|---------|
| `index_beir_datasets.py` | `beir-fiqa`, `beir-nfcorpus`, `beir-scifact` | Three [BEIR](https://github.com/beir-cellar/beir) corpora (100 docs each) |
| `index_browsecomp.py` | `browsecomp-plus` | [BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus) corpus (50 docs) |

## Prerequisites

- Python 3.9+
- An Elasticsearch endpoint and an API key.

## Setup

```bash
pip install -r requirements.txt
```

Provide your connection details via environment variables (each script falls
back to an interactive prompt if they are unset):

```bash
export ES_URL="https://your-deployment.es.cloud.es.io:443"
export ELASTIC_API_KEY="your-api-key"
```

## Run

```bash
python index_beir_datasets.py   # creates the three BEIR indices
python index_browsecomp.py      # creates the browsecomp-plus index
```

Each script deletes and recreates its indices before loading, so reruns are
idempotent. `index_browsecomp.py` skips indexing if `browsecomp-plus` already
holds documents.
