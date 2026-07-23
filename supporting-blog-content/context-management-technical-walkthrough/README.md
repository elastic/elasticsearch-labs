# Context management technical walkthrough — index setup & evaluation scripts

Standalone scripts that create and populate the four indices referenced in the `Context Management Technical Walkthrough` blog with 50 sample documents. 
This allows index creation and indexing of sample data to easily follow along with blog content. 

All four indices are BM25-only to save on inference costs, and are enriched with mapping metadata (`_meta.description` and per-field `meta.description`).

Alongside the setup scripts, a set of [evaluation scripts](#evaluating-with-agents-kis-vs-baseline) and a
[`query-ki` skill](#the-query-ki-skill) let you compare an agent answering with and without Knowledge Indicators (KIs).

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

## Evaluating with agents (KIs vs. baseline)

Four [deep agent](https://pypi.org/project/deepagents/) scripts let you see the difference Knowledge
Indicators make. They come in two pairs — one for each scenario in the blog — that ask the *same*
question through the *same* model, changing only how the agent retrieves context:

| Script | Scenario | Retrieval |
|--------|----------|-----------|
| `fact_baseline_agent.py` | Answer a fact question over `browsecomp-plus` | Raw ES\|QL over the documents (+ `get_mapping`) |
| `fact_ki_agent.py` | Same question | `query-ki` skill → `corpus_entry` fact KIs |
| `index_baseline_agent.py` | Route a question across `beir-fiqa` / `beir-nfcorpus` / `beir-scifact` | Raw ES\|QL; the agent must guess the right index |
| `index_ki_agent.py` | Same question | `query-ki` skill → `index_metadata_entry` routing KIs |

Each script invokes the agent on a sample question, prints the tool calls it made, and prints the final
answer — so you can compare both the answer quality and the number of queries needed.

> **Prerequisite:** the KI scripts read Knowledge Indicators from `ai-index-*` indices. Generate those
> first by running the walkthrough workflow described in the blog; the baseline scripts need only the
> sample data created above.

### Setup

```bash
pip install deepagents langchain-core langchain-openai
```

The scripts talk to any OpenAI-compatible chat endpoint, configured via `LLM_*` environment variables.
They default to OpenRouter with `anthropic/claude-sonnet-4.5`, so at minimum set an API key:

```bash
export LLM_API_KEY="your-key"
# optional overrides (defaults shown):
export LLM_BASE_URL="https://openrouter.ai/api/v1"
export LLM_MODEL="anthropic/claude-sonnet-4.5"
```

`ES_URL` and `ES_API_KEY` must also be set (these scripts read them directly — there is no interactive fallback).

### Run

Run from this folder so the KI agents can load the skill (they resolve `skills/` relative to the working directory):

```bash
python fact_baseline_agent.py
python fact_ki_agent.py
python index_baseline_agent.py
python index_ki_agent.py
```

### The `query-ki` skill

`skills/query-ki/SKILL.md` is a deepagents skill the two KI agents load via a `FilesystemBackend`. It
retrieves KIs from the `ai-index-*` indices with a single ES\|QL query (lexical + semantic match fused),
selecting `corpus_entry` for facts or `index_metadata_entry` for routing profiles.
