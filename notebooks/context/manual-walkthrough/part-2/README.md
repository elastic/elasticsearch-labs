# Context management manual walkthrough — Part 2: fact KIs over a corpus

Companion notebook for **Part 2** of the *Context management in Elasticsearch: a
technical walkthrough* blog series. It distills each `browsecomp-plus` document
into a `corpus_entry` Knowledge Indicator (KI) so an agent answers without reading
full documents — then compares an agent answering **with** and **without** those
fact KIs.

> Part 1 (routing with index-metadata KIs) lives in
> [`../part-1`](../part-1).

## What the notebook does

[`index-facts-kis.ipynb`](index-facts-kis.ipynb) runs end to end:

1. Indexes the `browsecomp-plus` corpus (BM25-only, 50 docs).
2. Creates an **AI Index** and generates one fact KI per document with a Kibana Workflow.
3. Writes a `query-ki` skill to disk and builds a deepagents agent around it.
4. Asks the same question with and without the fact KIs, printing the tool calls each makes so you can compare query counts and answer quality.

The notebook is self-contained — run it top to bottom.

> The fact workflow processes every indexed document sequentially in a single
> run, so it can take several minutes. Keep the sample at 50 documents — the
> example questions rely on specific documents being present.

## Prerequisites

- Python 3.9+
- An **Elasticsearch endpoint** and an **API key** (Elastic Cloud, serverless, or local).
- A **Kibana endpoint URL** for the Workflows API.
- A **GenAI connector** in Kibana for the workflow's `ai.agent` step.
- An **LLM API key** for any OpenAI-compatible endpoint (defaults to OpenRouter with `anthropic/claude-sonnet-4.5`).

The notebook writes its `skills/` directory and Jupyter checkpoints at runtime;
both are gitignored.

## Related

The blog's copy-paste index setup and agent-evaluation scripts live in
[`supporting-blog-content/context-management-technical-walkthrough-part-2`](../../../../supporting-blog-content/context-management-technical-walkthrough-part-2).
