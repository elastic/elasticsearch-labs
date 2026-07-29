# Context management technical walkthrough (Part 1): routing with index-metadata KIs

Standalone scripts for [Know Your Index: Context Management for Smarter AI Agents,
Powered by Elasticsearch AI Indices](https://www.elastic.co/search-labs/blog/context-management-technical-walkthrough-index-metadata),
Part 1 of the Context management technical walkthrough series. Part 1 covers
routing: it profiles each index into an `index_metadata_entry` Knowledge Indicator
(KI) so an agent picks the right index instead of guessing.

The scripts here create and populate the three [BEIR](https://github.com/beir-cellar/beir)
indices used in the blog, then let you compare an agent answering with and
without those routing KIs.

Part 2 (fact KIs over a single corpus) lives in
[`../context-management-technical-walkthrough-part-2`](../context-management-technical-walkthrough-part-2).

| Script | Indices | Dataset |
|--------|---------|---------|
| `index_beir_datasets.py` | `beir-fiqa`, `beir-nfcorpus`, `beir-scifact` | Three BEIR corpora, 50 docs each |

All indices are BM25-only to save on inference costs. Each one is enriched with
mapping metadata (`_meta.description` and per-field `meta.description`) so the
routing profiles have signal to work with.

## Notebook

A runnable notebook walks through this example end to end. It creates the AI
Index, generates the routing KIs with a Kibana Workflow, and compares an agent
answering with and without them:

- [`notebooks/context/manual-walkthrough/part-1/index-metadata-kis.ipynb`](../../notebooks/context/manual-walkthrough/part-1/index-metadata-kis.ipynb)

The notebook is self-contained: it writes its own `query-ki` skill and inlines
the agent harness, so you can run it top to bottom. Beyond the script
prerequisites below, it also needs a Kibana endpoint URL, a GenAI connector for
the workflow's `ai.agent` step, and an LLM API key for any OpenAI-compatible
endpoint.

## Prerequisites

- You need Python 3.9 or newer.
- You need an Elasticsearch endpoint and an API key (Elastic Cloud, serverless, or a local cluster).

## Steps

### 1. Clone the repo and change into the script folder

```bash
git clone https://github.com/elastic/elasticsearch-labs.git
cd elasticsearch-labs/supporting-blog-content/context-management-technical-walkthrough-part-1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs `elasticsearch>=9,<10` and `datasets`, the Hugging Face loader used
to stream the corpora.

### 3. Provide your connection details

Set them as environment variables:

```bash
export ES_URL="https://your-deployment.es.cloud.es.io:443"   # or http://localhost:9200
export ES_API_KEY="your-api-key"
```

Or skip this step. The script falls back to an interactive prompt if the
variables are not set, reading `ES_URL` via `input()` and the API key via a
hidden `getpass()` prompt.

To generate an API key on a local cluster, run:

```bash
curl -s -u elastic:<password> -X POST "http://localhost:9200/_security/api_key" \
  -H 'Content-Type: application/json' -d '{"name":"context-walkthrough"}'
```

Use the `encoded` value from the response.

### 4. Run the script

```bash
python index_beir_datasets.py   # creates beir-fiqa, beir-nfcorpus, beir-scifact (50 docs each)
```

The script prints the doc count per index when it finishes.

## Notes

The script is idempotent: `index_beir_datasets.py` deletes and recreates its
indices on every run.

To verify the indices, run:

```bash
curl -s -H "Authorization: ApiKey $ES_API_KEY" \
  "$ES_URL/_cat/indices/beir-*?v"
```

## Evaluating with agents (KIs vs. baseline)

Two [deep agent](https://pypi.org/project/deepagents/) scripts let you see the
difference routing KIs make. They ask the *same* question through the *same*
model, changing only how the agent retrieves context:

| Script | Retrieval |
|--------|-----------|
| `index_baseline_agent.py` | The agent runs raw ES\|QL and must guess the right index. |
| `index_ki_agent.py` | The agent calls the `query-ki` skill to load `index_metadata_entry` routing KIs. |

Each script invokes the agent on a sample question, prints the tool calls it
made, and prints the final answer, so you can compare both the answer quality and
the number of queries needed.

`index_ki_agent.py` reads Knowledge Indicators from the `ai-index-*` indices, so
generate those first by running the walkthrough workflow described in the blog
(or the notebook above). The baseline script needs only the sample data created
in step 4.

### Setup

```bash
pip install deepagents langchain-core langchain-openai
```

The scripts talk to any OpenAI-compatible chat endpoint, configured via `LLM_*`
environment variables. They default to OpenRouter with
`anthropic/claude-sonnet-4.5`, so at minimum set an API key:

```bash
export LLM_API_KEY="your-key"
# optional overrides (defaults shown):
export LLM_BASE_URL="https://openrouter.ai/api/v1"
export LLM_MODEL="anthropic/claude-sonnet-4.5"
```

`ES_URL` and `ES_API_KEY` must also be set. These scripts read them directly and
have no interactive fallback.

### Run

Run from this folder so the KI agent can load the skill. It resolves `skills/`
relative to the working directory:

```bash
python index_baseline_agent.py "your question"
python index_ki_agent.py "your question"
```

### The `query-ki` skill

`skills/query-ki/SKILL.md` is a deepagents skill that the KI agent loads via a
`FilesystemBackend`. It retrieves `index_metadata_entry` routing KIs from the
`ai-index-*` indices with a single ES\|QL query that fuses lexical and semantic
matches.
