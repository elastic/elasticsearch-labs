# Building a Multimodal RAG Pipeline with Elasticsearch: The Story of Gotham City

This repository contains the code for implementing a Multimodal Retrieval-Augmented Generation (RAG) system using Elasticsearch. The system processes and analyzes different types of evidence (images, audio, text, and depth maps) to solve a crime in Gotham City.

## Overview

The pipeline demonstrates how to:
- Generate unified embeddings for multiple modalities using ImageBind
- Store and search vectors efficiently in Elasticsearch
- Analyze evidence using GPT-4 to generate forensic reports

## Prerequisites

- Python 3.10+
- Elasticsearch cluster (cloud or local)
- OpenAI API key - Setup an OpenAI account and create a [secret key](https://platform.openai.com/docs/quickstart)
- 8GB+ RAM
- GPU (optional but recommended)

## Quick Start

1. **Setup Environment**
```bash
rm -rf .venv requirements.txt
python3 -m venv .venv
source .venv/bin/activate
pip install pip-tools
# Recreate requirements.txt
pip-compile
# Install main dependencies
pip install -r requirements.txt



python3 -m venv .venv
source .venv/bin/activate
pip install "python-dotenv[cli]"
pip install -r requirements-torch.txt
pip install -r requirements.txt

# Make sure you have pytorch installed and Python 3.10+
pip install torch torchvision torchaudio

# Create and activate virtual environment
python -m venv env_mmrag
source env_mmrag/bin/activate  # Unix/MacOS
# or
.\env_mmrag\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

2. **Configure Credentials**
Create a `.env` file:
```env
ELASTICSEARCH_ENDPOINT="your-elasticsearch-endpoint"
ELASTIC_API_KEY="your-elastic-api-key"
OPENAI_API_KEY="your-openai-api-key"
```

3. **Run the Demo**
```bash
# Verify file structure
python stages/01-stage/files_check.py

# Generate embeddings
python stages/02-stage/test_embedding_generation.py

# Index content
python stages/03-stage/index_all_modalities.py

# Search and analyze
python stages/04-stage/rag_crime_analyze.py
```

## Project Structure

```
├── README.md
├── requirements.txt
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

