# Hugging Face integrations notebooks

This folder contains notebooks that demonstrate how to work with Hugging Face hosted models in Elasticsearch.

The following notebooks are available:

- [Loading an NLP model from Hugging Face](#loading-an-nlp-model-from-hugging-face)

## Notebooks

### Loading an NLP model from Hugging Face

In the [`loading-model-from-hugging-face.ipynb`](./loading-model-from-hugging-face.ipynb) notebook you'll learn how to:

- Use the `eland` tool to import the [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model from Hugging Face.
- Index documents into Elasticsearch and generate text embeddings using an ingest pipeline.
- Transform search queries into vectors using the Hugging Face model and perform vector searches over the dataset.

