# Building a Multimodal RAG Pipeline with Elasticsearch: The Story of Gotham City

This repository contains the code for the blog [Building a multimodal Retrieval-Augmented Generation (RAG) system with Elasticsearch](https://www.elastic.co/search-labs/blog/building-multimodal-rag-system). The system processes and analyzes different types of evidence (images, audio, and text) to solve a crime in Gotham City.

## Overview

The pipeline demonstrates how to:
- Use a single `semantic_text` field backed by `jina-embeddings-v5-omni-small` through Elastic Inference Service (EIS)
- Ingest text, images, and audio in one index field and search semantically with text queries
- Analyze evidence using an OpenAI-compatible LLM to generate forensic reports

## Prerequisites

- Python 3.x
- Elastic Cloud Serverless Elasticsearch instance
- OpenAI-compatible API key (direct OpenAI key or LiteLLM virtual key)

## Elastic Cloud setup (free trial)

1. Sign up for an Elastic Cloud free trial at [cloud.elastic.co](https://cloud.elastic.co/registration).
2. Create an Elasticsearch Serverless instance.
3. In the deployment page, copy:
   - the **Elasticsearch endpoint** (use it as `ELASTICSEARCH_URL`)
   - an **API key** with `manage_inference` privileges (use it as `ELASTICSEARCH_API_KEY`)
4. Copy `env.example` to `.env` and set:
   - `ELASTICSEARCH_URL`
   - `ELASTICSEARCH_API_KEY`
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL` (optional, only when using LiteLLM proxy)

## Code execution 

We provide a Google Colab notebook that allows you to explore the entire pipeline interactively:
- [Open the Multimodal RAG Pipeline Notebook](01-mmrag-blog-quick-start.ipynb)
- This notebook includes step-by-step instructions and explanations for each stage of the pipeline


## Project Structure

```
├── README.md
├── requirements.txt
├── 01-mmrag-blog-quick-start.ipynb   # Jupyter notebook execution
├── src/
│   ├── elastic_manager.py       # Elasticsearch semantic_text operations
│   └── llm_analyzer.py         # OpenAI-compatible LLM integration
├── stages/
│   ├── 01-stage/              # File organization
│   ├── 02-stage/              # Embedding generation
│   ├── 03-stage/              # Elasticsearch indexing/search
│   └── 04-stage/              # Evidence analysis
└── data/                      # Sample data
    ├── images/
    ├── audios/
    └── texts/

```

## Sample Data

The repository includes sample evidence files:
- Images: Crime scene photos and security camera footage
- Audio: Suspicious sound recordings
- Text: Mysterious notes and riddles

## How It Works

1. **Evidence Collection**: Files are organized by modality in the `data/` directory
2. **Semantic Indexing**: Elasticsearch `semantic_text` (`content`) sends each evidence item to EIS (`.jina-embeddings-v5-omni-small`) during indexing
3. **Semantic Search**: Semantic queries (text, image, or audio) run directly against content with semantic matching
4. **Analysis**: An OpenAI-compatible LLM analyzes the connections between evidence to identify suspects

