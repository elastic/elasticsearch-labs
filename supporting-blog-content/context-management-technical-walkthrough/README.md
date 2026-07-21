# Context management technical walkthrough — index setup scripts

Standalone scripts that create and populate the four indices referenced in the `Context Management Technical Walkthrough` blog with 50 sample documents. 
This allows index creation and indexing of sample data to easily follow along with blog content. 

All four indices are BM25-only to save on inference costs, and are enriched with mapping metadata (`_meta.description` and per-field `meta.description`).

| Script | Indices | Dataset |
|--------|---------|---------|
| `index_beir_datasets.py` | `beir-fiqa`, `beir-nfcorpus`, `beir-scifact` | Three [BEIR](https://github.com/beir-cellar/beir) corpora (50 docs each) |
| `index_browsecomp.py` | `browsecomp-plus` | [BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus) corpus (50 docs) |

## Prerequisites

- Python 3.9+
- An Elasticsearch endpoint and an API key (Elastic Cloud, serverless, or a local cluster).

## Steps

### 1. Clone the repo and change into the script folder

```bash
git clone https://github.com/elastic/elasticsearch-labs.git
cd elasticsearch-labs/supporting-blog-content/context-management-technical-walkthrough
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs `elasticsearch>=9,<10` and `datasets` (the Hugging Face loader used
to stream the corpora).

### 3. Provide your connection details

Set them as environment variables:

```bash
export ES_URL="https://your-deployment.es.cloud.es.io:443"   # or http://localhost:9200
export ES_API_KEY="your-api-key"
```

Or skip this step — each script falls back to an interactive prompt (`ES_URL` via
`input()`, the API key via a hidden `getpass()` prompt) if the variables aren't set.

> Generating an API key on a local cluster:
>
> ```bash
> curl -s -u elastic:<password> -X POST "http://localhost:9200/_security/api_key" \
>   -H 'Content-Type: application/json' -d '{"name":"context-walkthrough"}'
> ```
>
> Use the `encoded` value from the response.

### 4. Run the scripts

```bash
python index_beir_datasets.py   # creates beir-fiqa, beir-nfcorpus, beir-scifact (50 docs each)
python index_browsecomp.py      # creates browsecomp-plus (50 docs)
```

Each script prints the doc count per index when it finishes. The BrowseComp run
takes longer on first use because it streams a shard of the ~1.76 GB corpus from
Hugging Face before indexing.

## Notes

- **Idempotent:** `index_beir_datasets.py` deletes and recreates its indices on
  every run. `index_browsecomp.py` skips indexing if `browsecomp-plus` already
  contains documents (delete the index first if you want a clean reload).
- **Verify:**

  ```bash
  curl -s -H "Authorization: ApiKey $ES_API_KEY" \
    "$ES_URL/_cat/indices/beir-*,browsecomp-plus?v"
  ```
