# Context management manual walkthrough, Part 2: fact KIs over a corpus

Companion notebook for [Know Your Facts: Context Management for Smarter AI Agents,
Powered by Elasticsearch AI Indices](https://www.elastic.co/search-labs/blog/context-management-technical-walkthrough-facts),
Part 2 of the Context management technical walkthrough series. It distills each `browsecomp-plus` document
into a `corpus_entry` Knowledge Indicator (KI) so an agent answers without
reading full documents, then compares an agent answering with and without those
fact KIs.

Part 1 (routing with index-metadata KIs) lives in [`../part-1`](../part-1).

## What the notebook does

[`index-facts-kis.ipynb`](index-facts-kis.ipynb) runs end to end:

1. It indexes the `browsecomp-plus` corpus, BM25-only, 50 docs.
2. It creates an AI Index and generates one fact KI per document with a Kibana Workflow.
3. It writes a `query-ki` skill to disk and builds a deepagents agent around it.
4. It asks the same question with and without the fact KIs, printing the tool calls each makes so you can compare query counts and answer quality.

The notebook is self-contained, so run it top to bottom.

The fact workflow processes every indexed document sequentially in a single run,
so it can take several minutes. Keep the sample at 50 documents, since the
example questions rely on specific documents being present.

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
[`supporting-blog-content/context-management-technical-walkthrough-part-2`](../../../../supporting-blog-content/context-management-technical-walkthrough-part-2).
