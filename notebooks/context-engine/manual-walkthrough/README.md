# Context Engine — manual walkthrough

This folder contains notebooks that walk through the **Context Engine** by hand: indexing a dataset, creating Knowledge Items (KIs) with Kibana Workflows, retrieving them through the `get_context` API, and consuming them from an external agent harness.

A **Knowledge Item (KI)** is a small, semantically searchable chunk of information stored in the Context Engine. KIs come in two flavors, and these notebooks cover both:

- **Index-level KIs** — profile *what an index contains*, so an agent can pick the right index to query (index selection / routing).
- **Document-level KIs** — extract individual *facts* out of documents, so an agent can retrieve an answer.

The metadata notebook uses three [BEIR benchmark](https://github.com/beir-cellar/beir) corpora (financial Q&A, biomedical, scientific fact-checking) to demonstrate index routing across distinct domains. The facts notebook uses the [BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus) corpus to demonstrate per-document KI extraction. Both are indexed BM25-only for speed.

> In the Kibana source the Context Engine is sometimes called **SML** / the **semantic metadata layer** — it is the same thing.

## Prerequisites

These notebooks exercise the Context Engine, Workflows, and the `ai.agent` step against an Elastic Cloud deployment:

- An **Elastic Cloud** deployment where the Context Engine is available. The notebooks connect with your **Cloud ID** and an **API key** (the Kibana URL is derived from the Cloud ID).
- The notebooks **explicitly enable** the `agentBuilder:experimentalFeatures` feature flag — don't assume it's on.
- A **GenAI connector** configured in Kibana (Stack Management → Connectors) for the `ai.agent` workflow step.
- For the agent harness in `index-facts-kis.ipynb`, an **Anthropic API key** (the deep agent runs on Claude Haiku via `langchain-anthropic`).

## Notebooks

The following notebooks are available:

1. [Index-selection KIs](#1-index-selection-kis)
2. [Document-level fact KIs + an agent harness](#2-document-level-fact-kis--an-agent-harness)

### 1. Index-selection KIs

In the [`index-metadata-kis.ipynb`](./index-metadata-kis.ipynb) notebook you'll learn how to:

- Connect to Elastic Cloud and enable the Context Engine feature flag.
- Index small slices of three BEIR benchmark datasets (BM25 only) — financial Q&A, biomedical research, and scientific fact-checking — each enriched with mapping metadata (`_meta.description` and per-field `meta.description`).
- Run a Kibana Workflow once per index, chaining `elasticsearch.request` (read the mapping) + `elasticsearch.search` (sample docs) → `ai.agent` (structured **index profile**) → `contextEngine.addEntry` to write an index-level KI.
- Retrieve the KIs through the `get_context` API and see domain-specific queries routed to the correct index.

### 2. Document-level fact KIs + an agent harness

In the [`index-facts-kis.ipynb`](./index-facts-kis.ipynb) notebook you'll learn how to:

- Index BrowseComp-Plus documents (BM25 only).
- Run a Kibana Workflow that, for each document, chains `ai.agent` (structured-output KI extraction) → `contextEngine.addEntry` to create one fact KI per document.
- Retrieve fact KIs through the `get_context` API.
- Wrap `get_context` as a tool inside a [LangChain deep agents](https://pypi.org/project/deepagents/) harness, with system-prompt guidance on when to call it, and watch the agent answer a question by retrieving from the Context Engine.

Each notebook ends with a cleanup section that removes the KIs, the workflow, and the index it created.
