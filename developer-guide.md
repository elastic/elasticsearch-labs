# Elasticsearch Developer Guide

## Table of Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Setup Elasticsearch](#setup-elasticsearch)
  - [With Docker](#use-elasticsearch-with-docker)
  - [Elastic Cloud](#use-elasticsearch-with-elastic-cloud)
- [API Client](#client)
  - [Python](#python)

## Introduction

This guide is intended for developers who want to use the Gen AI with Elasticsearch API to build applications that use the Gen AI with Elasticsearch service.

Elasticsearch is a search database that allows you to store and retrieve relevant information extremely quickly. It is used by many of the world's largest companies to power their search and analytics applications.

Elasticsearch supports many different types of queries, including vector search, full-text search, geospatial search, and more.

### Can Elasticsearch support Vector Search?

Yes! Elasticsearch supports vector search through the [dense_vector](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html) data type.

### Can I do Semantic Search with Elasticsearch?

Yes! With using an embedding model like [sentence-transformers](https://www.sbert.net/) you can transform your text into a vector and store it in Elasticsearch. Then you can use Elasticsearch's vector search capabilities to find similar documents.

### Can I combine both Semantic Search and Full-Text Search?

Yes! You can combine both Semantic Search and Full-Text Search via a "hybrid" query strategy. You retrieve relevant documents through both a vector search and a full-text search, and then balance the scores from both queries to get the final ranking of documents.

### Get started

To get started, [go to the quickstart guide](#quick-start) to setup Elasticsearch and start using the API Client.

## Quick Start

This guide explains how to index and search

**NOTE** This guide assumes you have got [Elasticsearch setup](#setup), you can start using the API Client to index and search documents.

You can quick start in three ways:

- Use the [Quick Start notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/00-quick-start.ipynb) to index and perform Semantic search with Elasticsearch.
- Follow the commands below in your local development environment.

### Create an Index

An index is a collection of documents that have similar characteristics. For example, you might have an index for "products" and another index for "users".

Below lets create an index called "demo" with a mapping for the "text" field. With this mapping, we will be able to store 8 dimentional vectors in the "text" field. When we search for similar documents, we will use the "cosine" similarity function.

```python
es.indices.create(index="demo", mappings={
  "properties": {
    "text": {
      "type": "dense_vector",
      "dims": 8
      "similarity": "cosine"
      "index": True
    }
  }
})
```

To check if the index was created, you can run the following command:

```python
es.indices.get(index="demo")
```

### Index Documents

Lets start by ingesting vectors into your index, using the bulk helper.

```python
from elasticsearch.helpers import bulk

docs = [
  { "text": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], "title": "Document 1"},
  { "text": [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4], "title": "Document 2"},
  { "text": [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3], "title": "Document 3"}
]

actions = []
for doc in docs:
  action = {
      "_index": "demo",
      "_source": doc
  }
  actions.append(action)

bulk(es, actions, refresh=True)

```

We use `refresh` to make sure the documents are available for search immediately.

### Search for Similar Documents

Now that we have indexed some documents, we can search for similar documents that are most similar to the query vector.

We will calculate the distance with the cosine similarity function, and return the top 10 most similar documents.

```python
response = es.search(index="demo", body={
    "knn": {
      "field": "text",
      "query_vector": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
      "k": 10,
      "num_candidates": 100
    }
})

```

# Setup

Take you through the steps to setup and connect to Elasticsearch.

## Running Elasticsearch

You can start using Elasticsearch really quickly. We highlight two of the most common ways to use Elasticsearch below.

### Example: Use Elasticsearch with Docker

Recommended for local development and testing.

The quickest way to get started developing with Elasticsearch is to use Docker. Run the following command to download and launch the official Elasticsearch Docker image:

```bash
docker run -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "xpack.security.http.ssl.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.9.0
```

Elasticsearch is now running on http://localhost:9200

### Example: Use Elasticsearch with Elastic Cloud

Recommended for production.

Elastic Cloud is the official hosted and managed Elasticsearch service, offering Elasticsearch, Kibana, APM, and much more. Elastic Cloud is available on AWS, GCP, and Azure.

You can sign up for a free 14-day trial at https://cloud.elastic.co

## API Clients

Elasticsearch supports a number of REST clients for different languages.

- Python [view docs](https://elasticsearch-py.readthedocs.io/en/master/)
- Javascript [view docs](https://www.elastic.co/guide/en/elasticsearch/client/javascript-api/current/getting-started-js.html)

For other clients, see [Client Libraries](https://www.elastic.co/guide/en/elasticsearch/client/index.html).

### Install

To install the client, run the following command:

Python

```bash
pip install elasticsearch
```

### Connecting to Elasticsearch

Showing both Python and Javascript examples.

- [Localhost example](#example-localhost)
- [Elastic Cloud with API Key example](#example-elastic-cloud-with-api-key)
- [Elastic Cloud with Username and Password example](#example-elastic-cloud-with-username-and-password)

#### Example: Localhost

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])
```

#### Example: Elastic Cloud with API Key

You can create an API key in Kibana by going to:

1. Management > Stack Management > Security > API Keys
2. Click "Create API Key"
3. Give the API Key a name and click "Create"
4. Copy the API key (base64 encoded)

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(
  cloud_id="YOUR_CLOUD_ID",
  api_key="YOUR_API_KEY"
)
```

#### Example: Elastic Cloud with Username and Password

The password is given to you when you create your Elastic Cloud deployment. If you don't have it, you can reset it by going to:

1. Elastic Cloud Console > Deployment > Security > Reset Password
2. Copy the password

This will reset the password for the `elastic` user.

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(
  cloud_id="YOUR_CLOUD_ID",
  http_auth=("elastic", "<password>"),
)
```

### Validate Connection

To validate that you have connected to Elasticsearch, run the following command.

This should return cluster information if setup was successful.

Python

```python
es.info()
```

# Indexing & Searching

## Create an Index

An index is a collection of documents that have similar characteristics. For example, you might have an index for "products" and another index for "users".

### Example: Create an Index with a Dense Vector Mapping

```python
es.indices.create(index="demo", mappings={
  "properties": {
    "text": {
      "type": "dense_vector",
      "dims": 8
      "similarity": "cosine"
      "index": True
    }
  }
})
```

By default, Elasticsearch will create field mappings automatically for you, detecting the type of data you are indexing. You can read more about [dynamic mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-field-mapping.html).

You can also create your own mappings, for complex data types like geo points and dense vectors. You can read more about [field data types](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html).

### Example: Create an Index with title & price fields

```python
es.indices.create(index="demo", mappings={
  "properties": {
    "title": {
      "type": "text"
    },
    "price": {
      "properties": {
        "amount": {
          "type": "float"
        },
        "currency": {
          "type": "keyword"
        }
      }
    }
  }
})
```

## Inserting Documents

You can insert documents into an index using the `index` for a single document, or `bulk` for multiple documents.

### Example: Insert a Single Document

```python

doc = {
  "text": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
  "title": "Document 1"
}

es.index(index="demo", document=doc)
```

### Example: Insert Multiple Documents

In this example, we use the `bulk` helper function to insert multiple documents at once.

Helpers also provide a `parallel_bulk` function that can be used to insert documents in parallel and a `streaming_bulk` function that can be used to insert documents in a streaming fashion.

Read more about [helpers](https://elasticsearch-py.readthedocs.io/en/stable/helpers.html).

```python
from elasticsearch.helpers import bulk

docs = [
  { "text": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], "title": "Document 1"},
  { "text": [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4], "title": "Document 2"},
  { "text": [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3], "title": "Document 3"}
]

actions = []
for doc in docs:
  action = {
      "_index": "demo",
      "_source": doc
  }
  actions.append(action)

bulk(es, actions, refresh=True)

```

## Searching

# Data Modelling

# Tweaking Relevance

## Semantic Search

## Text Search

## Hybrid Search

## Search with Sparse Vector

ELSER Examples

## Boosting & Re-ranking

# Filtering

## Keyword Filtering

## Range Filtering

## Date Filtering

## Geo Filtering

# Integrations

## OpenAI

## Hugging Face

## Langchain

## Llama-index
