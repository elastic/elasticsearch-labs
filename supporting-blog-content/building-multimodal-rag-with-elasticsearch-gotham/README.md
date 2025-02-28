# Building a Multimodal RAG Pipeline with Elasticsearch: The Story of Gotham City

This repository contains the code for implementing a Multimodal Retrieval-Augmented Generation (RAG) system using Elasticsearch. The system processes and analyzes different types of evidence (images, audio, text, and depth maps) to solve a crime in Gotham City.

## Overview

The pipeline demonstrates how to:
- Generate unified embeddings for multiple modalities using ImageBind
- Store and search vectors efficiently in Elasticsearch
- Analyze evidence using GPT-4 to generate forensic reports

## Prerequisites

- Python 3.x
- Elasticsearch cluster (cloud or local)
- OpenAI API key - Setup an OpenAI account and create a [secret key](https://platform.openai.com/docs/quickstart)
- 8GB+ RAM
- GPU (optional but recommended)

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
│   ├── embedding_generator.py   # ImageBind wrapper
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
    ├── texts/
    └── depths/

```

## Sample Data

The repository includes sample evidence files:
- Images: Crime scene photos and security camera footage
- Audio: Suspicious sound recordings
- Text: Mysterious notes and riddles
- Depth Maps: 3D scene captures

## How It Works

1. **Evidence Collection**: Files are organized by modality in the `data/` directory
2. **Embedding Generation**: ImageBind converts each piece of evidence into a 1024-dimensional vector
3. **Vector Storage**: Elasticsearch stores embeddings with metadata for efficient retrieval
4. **Similarity Search**: New evidence is compared against the database using k-NN search
5. **Analysis**: GPT-4 analyzes the connections between evidence to identify suspects

