# Unsupervised Document Clustering with Elasticsearch and Jina Embeddings

Companion notebook for the Elastic Search Labs blog post.

## What's included

- `clustering_tutorial.ipynb` — Full runnable notebook
- `app/` — Supporting Python modules (clustering, labeling, indexing, visualization)
- `elastic/templates/` — Elasticsearch index mapping template
- `.env.example` — Required environment variables
- `requirements.txt` — Python dependencies

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
jupyter notebook clustering_tutorial.ipynb
```

## Requirements

- Python 3.11+
- Elasticsearch 8.18+ (for `bbq_disk`), 9.3+ or Serverless (for diversify retriever)
- [Jina API key](https://jina.ai/embeddings/) (free tier: 10M tokens)
- [Guardian API key](https://bonobo.capi.gutools.co.uk/register/developer) (free)
