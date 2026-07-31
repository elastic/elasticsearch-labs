# Precomputed context technical walkthrough (Part 1): routing with index-metadata KIs

A runnable notebook for [Know Your Index: Precomputed Context for Smarter AI Agents,
Powered by Elasticsearch AI Indices](https://www.elastic.co/search-labs/blog/context-management-technical-walkthrough-index-metadata),
Part 1 of the Precomputed context technical walkthrough series. Part 1 covers
routing: it profiles each index into an `index_metadata_entry` Knowledge Indicator
(KI) so an agent picks the right index instead of guessing.

The notebook creates and populates the three [BEIR](https://github.com/beir-cellar/beir)
indices used in the blog, then lets you compare an agent answering with and
without those routing KIs.

Part 2 (fact KIs over a single corpus) lives in
[`../precomputed-context-technical-walkthrough-part-2`](../precomputed-context-technical-walkthrough-part-2).

| Index | Domain | Dataset |
|-------|--------|---------|
| `beir-fiqa` | Financial Q&A | [FiQA](https://huggingface.co/datasets/BeIR/fiqa) |
| `beir-nfcorpus` | Biomedical / nutrition | [NFCorpus](https://huggingface.co/datasets/BeIR/nfcorpus) |
| `beir-scifact` | Scientific fact-checking | [SciFact](https://huggingface.co/datasets/BeIR/scifact) |

All indices are BM25-only to save on inference costs (50 docs each). Each one is
enriched with mapping metadata (`_meta.description` and per-field
`meta.description`) so the routing profiles have signal to work with.

## Notebook

The walkthrough is a single notebook that runs end to end:

- [`index-metadata-kis.ipynb`](./index-metadata-kis.ipynb)

It creates the AI Index, generates the routing KIs with a Kibana Workflow, and
compares an agent answering with and without them. The notebook is
self-contained: it writes its own `query-ki` skill and inlines the agent
harness, so you can run it top to bottom.

## Prerequisites

This notebook is designed to run against an Elastic Serverless project, where the
`ai-index-` component templates and Kibana Workflows are available. If you don't
have one, [sign up for a trial](https://cloud.elastic.co/registration?onboarding_token=search&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=search-labs).

Before you start, have ready:

- Your Elasticsearch and Kibana endpoint URLs and an Elastic API key. If you
  don't have a key, [create one using these instructions](https://www.elastic.co/search-labs/tutorials/install-elasticsearch/elastic-cloud#creating-an-api-key).
- A GenAI connector configured in Kibana (Stack Management → Connectors) for the
  workflow's `ai.agent` step. Serverless projects come pre-configured with the
  Elastic Inference Service and a default connector.
- An API key for any OpenAI-compatible endpoint, used by the deep agent harness.
  Tested with OpenRouter API keys.

## Run it

Open the notebook in Colab (badge at the top of the notebook) or run it locally
with Jupyter. The first cell installs its own dependencies, and the notebook
prompts for the endpoints and API keys above as you go — nothing to configure
beforehand.
