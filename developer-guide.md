# Elasticsearch Developer Guide

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Setup](#setup-elasticsearch)
  - [Setup Elasticsearch](#running-elasticsearch)
    - [With Docker](#example:-use-elasticsearch-with-docker)
    - [Elastic Cloud](#use-elasticsearch-with-elastic-cloud)
  - [API Clients](#api-clients)
    - [Install](#install)
    - [Connecting to Elasticsearch](#connecting-to-elasticsearch)
      - [Localhost](#example-localhost)
      - [Elastic Cloud with API Key](#example-elastic-cloud-with-api-key)
      - [Elastic Cloud with Username and Password](#example-elastic-cloud-with-username-and-password)
    - [Validate Connection](#validate-connection)
- [Indexing & Querying](#indexing--querying)
  - [Create an Index](#create-an-index)
  - [Inserting Documents](#inserting-documents)
  - [Querying Documents](#querying-documents)
- [Data Modeling](#data-modeling)
  - [Long unstructured text](#long-unstructured-text)
- [Tweaking Relevance](#tweaking-relevance)
  - [Semantic Search](#semantic-search)
  - [Text Search](#text-search)
  - [Hybrid Search](#hybrid-search)
  - [Search with Sparse Vector and ELSER](#search-with-sparse-vector-and-elser)
  - [Boosting & Re-ranking](#boosting--re-ranking)
- [Filtering](#filtering)

# Integrations

- [Integrations](#integrations)
  - [OpenAI](#openai)
  - [Hugging Face](#hugging-face)
  - [Langchain](#langchain)

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

You can quick start in two ways:

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
  -e "run.license_type=trial" \
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

# Indexing & Querying

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

## Querying Documents

Once you have indexed documents, you can search for them using the `search` API.

### Example: Query for Similar Documents

In this example, we search for similar documents to the query vector.

```python

response = es.search(index="demo", body={
    "knn": {
      "field": "text",
      "query_vector": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
      "k": 10, # return top 10 most similar documents
      "num_candidates": 100
    }
})

```

### Example: Using model in Elasticsearch

In this example, instead of passing the query vector, we pass the query text and Elasticsearch will use the embedding model deployed in Elasticsearch to transform the text into a vector.

To deploy the model in Elasticsearch, follow the instructions in the [Deploying a Model](#deploying-a-model) section.

```python

response = es.search(index="demo", body={
    "knn": {
      "field": "text",
      "k": 10,
      "num_candidates": 50,
      "query_vector_builder": {
        "text_embedding": {
          "model_id": "sentence-transformers__all-minilm-l6-v2", # model id deployed in Elasticsearch
          "model_text": "example query"
        }
      }
    }
  }
)

```

# Data Modeling

Depending on the type of use-case you are building, you will need to model your data differently.

## Long unstructured text

If each document contains long text, you should consider breaking up the text into smaller chunks called passages. Long text are hard to represent as a single vector, especially if the text is about multiple topics. We recommend breaking up the text into smaller chunks, and indexing each passage as a separate document.

Breaking up the text into passages allows you to retrieve more relevant results, as you can find the most relevant passages in one or more documents that match the query.

Another advantage is for RAG use-cases, being able to pass in smaller relevant passages to the RAG model, instead of the entire document, will improve the quality of the answer and avoid hitting the token limits of the RAG model.

### Example: Chunking long text into passages

```python
# TODO
```

# Tweaking Relevance

Now that you are able to index and search documents, lets start to tweak the relevance of your search results.

## Semantic Search

With using an text embedding model like [sentence-transformers](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) you can transform your text into a vector that capture semantic information. These vectors represent the contextual meaning of sentences. When your customer's search for a query, you can transform the query into a vector and search for similar documents.

**NOTE** You must use the same embedding model to encode your documents and queries.

Follow along with the [Semantic Search Quick Start Notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/00-quick-start.ipynb)

### Example: Semantic Search with Elasticsearch

```python

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

response = es.search(index="demo", body={
    "knn": {
      "field": "text",
      "query_vector": model.encode("javascript books?"),
      "k": 10,
      "num_candidates": 100
    }
})

```

## Text Search

With BM25, you can retrieve relevant documents based on the keywords in the query, matching the keywords in the document. This is useful for retrieving documents that are relevant to the query (although may not be semantically similar). The advantage of using BM25 is that it is very fast, and can be used to retrieve relevant documents in milliseconds.

Follow along with [Text search notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/01-keyword-querying-filtering.ipynb).

### Example: Text Search with Elasticsearch

```python

response = es.search(index="demo", body={
    "query": {
      "match": {
        "title": "javascript books?"
      }
    }
})

```

## Hybrid Search

Elasticsearch allows you to combine both semantic search and text search in a single query. Using this technique, you tend to get better retrieval accuracy than if just using by vector similarity alone. This gives you the ability to retrieve documents that are both semantically similar and lexically close to the query.

Follow along with [hybrid search notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/02-hybrid-search.ipynb).

### Example: Hybrid Search with Elasticsearch

**note** This example uses [Reciprocal Rank Fusion](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) to balance the scores from both the vector search and text search with different relevance indicators into a single result set. Requires Elasticsearch 8.8.0+

```python

response = es.search(index="demo", body={
    "query": {
      "match": {
        "title": "javascript books?"
      }
    },
    "knn": {
      "field": "text",
      "query_vector": model.encode("javascript books?"),
      "k": 10,
      "num_candidates": 100
    },
    "rank" : {
      "rrf" : {}
    }
  }
)

```

## Search with Sparse Vector and ELSER

Elasticsearch has a retrieval model trained by Elastic that enables you to perform semantic search to retrieve relevant documents. To learn more about ELSER, see [ELSER Guide](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html).

To use, you must first deploy the ELSER model into Elasticsearch. Follow the instructions on how to [deploy ELSER model](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html#download-deploy-elser).

Follow along with [ELSER notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/03-ELSER.ipynb).

## Boosting & Re-ranking

TODO Notebook

# Filtering

Filtering allows you to filter the results of your query based on certain criteria. Filtering doesn't affect the score of the documents, but allows you to filter out documents that don't match the criteria, which should improve the performance of your query.

Follow along with [Filtering notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/02-keyword-querying-filtering.ipynb).

# Integrations

## OpenAI

Elasticsearch is commonly used with OpenAIs APIs in two ways:

- OpenAI's embedding model "text-embedding-ada-002" to transform text into a vector
- OpenAI's completion model to help answer questions given a context of documents retrieved from Elasticsearch

You can follow along with the [OpenAI notebooks]((https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/integrations/openai)

## Hugging Face

Hugging Face serves as an open-source hub dedicated to AI/ML models and tools, offering access to a vast collection of over 100,000 machine learning models. This platform presents a remarkable avenue for seamlessly incorporating specialized AI and ML functionalities into your applications.

Utilizing Hugging Face models with Elasticsearch can be achieved through two ways:

Transformers Python Library: Leverage the Transformers Python library to carry out inference within a Python backend environment. [Notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/00-quick-start.ipynb)

Hosted Models in Elasticsearch: Deploy Hugging Face models directly into Elasticsearch to perform inference within the Elasticsearch environment. [Notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/integrations/hugging-face/loading-model-from-hugging-face.ipynb)

## Langchain

LangChain is a popular framework for working with AI, Vectors, and embeddings. Used to simplify building a variety of AI applications.

Elasticsearch can be used with LangChain in two ways:

- Langchain VectorStore to store and retrieve documents from Elasticsearch
- Langchain self-query retriever to with the help of an LLM like OpenAI, transform a user's query into a query + filter to retrieve relevant documents from Elasticsearch.

You can follow along with the [Langchain notebooks](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/integrations/langchain)
