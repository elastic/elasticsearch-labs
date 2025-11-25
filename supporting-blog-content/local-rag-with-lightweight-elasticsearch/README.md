# Build a Local lightweight RAG System with Elasticsearch

Simple RAG (Retrieval-Augmented Generation) system using Elasticsearch for semantic search and Local AI as model provider. This application serves as supporting content for the blog post [Build a Local lightweight RAG System with Elasticsearch](https://www.elastic.co/search-labs/blog/local-rag-with-lightweight-elasticsearch)

## Prerequisites

- Docker
- Python 3.11+

## Quick Start

### 1. Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate 
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create an `.env` and put there your settings:

```yaml
# Elasticsearch Configuration
ES_URL=http://localhost:9200
ES_API_KEY="your_elasticsearch_api_key_here"
INDEX_NAME=team-data

# Local AI Configuration
LOCAL_AI_URL=http://localhost:8080/v1

# Dataset Configuration
DATASET_FOLDER=./Dataset
```

### 4. Run the Script

```bash
python script.py
```


