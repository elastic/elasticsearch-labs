# Building a Multimodal RAG Pipeline with Elasticsearch: The Story of Gotham City

This repository contains the code for the blog [Building a multimodal etrieval-Augmented Generation (RAG) system with Elasticsearch](https://www.elastic.co/search-labs/blog/building-multimodal-rag-system). The system processes and analyzes different types of evidence (images, audio, and text) to solve a crime in Gotham City.

## Overview

The pipeline demonstrates how to:
- Generate unified embeddings for multiple modalities using the `jina-embeddings-v5-omni-small` model through Elastic Inference Service (EIS)
- Store and search vectors efficiently in Elasticsearch
- Analyze evidence using GPT-4 to generate forensic reports

## Prerequisites

- Python 3.x
- Elasticsearch 9.4+ cluster (Elastic Cloud recommended)
- OpenAI-compatible API key (direct OpenAI key or LiteLLM virtual key)

## Elastic Cloud setup (free trial)

1. Sign up for an Elastic Cloud free trial at [cloud.elastic.co](https://cloud.elastic.co/registration).
2. Create an Elasticsearch deployment (9.4+).
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
- [Open the Multimodal RAG Pipeline Notebook](notebook/01-mmrag-blog-quick-start.ipynb)
- This notebook includes step-by-step instructions and explanations for each stage of the pipeline


## Project Structure

```
├── README.md
├── requirements.txt
├── notebook/
│   ├── 01-mmrag-blog-quick-start.ipynb   # Jupyter notebook execution
├── src/
│   ├── embedding_generator.py   # EIS embedding wrapper
│   ├── elastic_manager.py       # Elasticsearch operations
│   └── llm_analyzer.py         # GPT-4 integration
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
2. **Embedding Generation**: EIS (`jina-embeddings-v5-omni-small`) converts each piece of evidence into a 1024-dimensional vector
3. **Vector Storage**: Elasticsearch stores embeddings with metadata for efficient retrieval
4. **Similarity Search**: New evidence is compared against the database using k-NN search
5. **Analysis**: GPT-4 analyzes the connections between evidence to identify suspects

