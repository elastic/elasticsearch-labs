# Context management manual walkthrough, Part 1: routing with index-metadata KIs

Companion notebook for Part 1 of the *Context management in Elasticsearch: a
technical walkthrough* blog series. It profiles three BEIR indices into
`index_metadata_entry` Knowledge Indicators (KIs) so an agent routes to the right
index instead of guessing, then compares an agent answering with and without
those routing KIs.

Part 2 (fact KIs over a single corpus) lives in [`../part-2`](../part-2).

## What the notebook does

[`index-metadata-kis.ipynb`](index-metadata-kis.ipynb) runs end to end:

1. It indexes the three BEIR corpora (`beir-fiqa`, `beir-nfcorpus`, `beir-scifact`), BM25-only, 50 docs each.
2. It creates an AI Index and generates one routing profile KI per source index with a Kibana Workflow.
3. It writes a `query-ki` skill to disk and builds a deepagents agent around it.
4. It asks the same question with and without the routing KIs, printing the tool calls each makes so you can compare query counts and answer quality.

The notebook is self-contained, so run it top to bottom.

## Prerequisites

- You need Python 3.9 or newer.
- You need an Elasticsearch endpoint and an API key (Elastic Cloud, serverless, or local).
- You need a Kibana endpoint URL for the Workflows API.
- You need a GenAI connector in Kibana for the workflow's `ai.agent` step.
- You need an LLM API key for any OpenAI-compatible endpoint. It defaults to OpenRouter with `anthropic/claude-sonnet-4.5`.

The notebook writes its `skills/` directory and Jupyter checkpoints at runtime.
Both are gitignored.

## Related

The blog's copy-paste index setup and agent-evaluation scripts live in
[`supporting-blog-content/context-management-technical-walkthrough-part-1`](../../../../supporting-blog-content/context-management-technical-walkthrough-part-1).
