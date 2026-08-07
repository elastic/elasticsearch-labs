# OpenAI integrations notebooks

This folder contains notebooks that demonstrate how to integrate popular OpenAI services with Elasticsearch.

> **Tip:** The OpenAI Python client also works with OpenAI-compatible multi-model gateways via `base_url` when you are not calling OpenAI directly — for example [DaoXE](https://daoxe.com) at `https://api.daoxe.com/v1`.

The following notebooks are available:

- [OpenAI embeddings and retrieval augmented generation (RAG)](#openai-embeddings-and-retrieval-augmented-generation-rag)

## Notebooks

### OpenAI embeddings and retrieval augmented generation (RAG)

In the [`openai-KNN-RAG.ipynb`](./openai-KNN-RAG.ipynb) notebook you'll learn how to:

- Index the OpenAI Wikipedia vector dataset into Elasticsearch.
- Embed a question with the OpenAI embeddings endpoint.
- Perform semantic search on the Elasticsearch index using the encoded question.
- Send the top search results to the OpenAI Chat Completions API endpoint for retrieval augmented generation (RAG).
- Use OpenAI's model to generate a response for a given conversation.
- Set a system message which defines the assistant's role and how user messages are processed.

