# Self-querying retrieval with Elasticsearch

This script will show you how to ingest and create embeddings for documents which will then be used as part of a self-querying retriever

> **Tip:** To learn more about Elastic Cloud and how to use it, visit: [https://www.elastic.co/pt/cloud](https://www.elastic.co/pt/cloud)

## Prerequisites

- **Elasticsearch v8.16** (recommended): To support the latest semantic search features, this script in its current form utilizes Elastic Cloud but can be modified for self-managed
- **Python 3.x**
- **API Access to an LLM and embedding model**: This script requires an LLM for the retriever as well as an embedding model for creating vectors in our documents, the script assumes usage of Azure OpenAI but this can easily changed to another cloud based LLM or local one like Llama 3.
- **Python Libraries**: Required libraries are listed in the `requirements.txt` file.

To install the dependencies, use the following command:

```bash
pip install -r requirements.txt
```

or run the following individual pip commands:

# Core LangChain library
```bash
pip install langchain
```
# OpenAI integration for LangChain (Azure OpenAI support)
```bash
pip install langchain-openai
```
# Elasticsearch integration for LangChain
```bash
pip install langchain-elasticsearch
```
# Elasticsearch Python client (required for ElasticsearchStore)
```bash
pip install elasticsearch
```
# Additional dependencies for embeddings and document handling
```bash
pip install langchain-core langchain-community
```

```bash
pip install lark
```
