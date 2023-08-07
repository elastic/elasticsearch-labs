# Search notebooks

This folder contains a number of notebooks that demonstrate the fundamentals of Elasticsearch, like indexing embeddings, running lexical, semantic and _hybrid_ searches, and more.

The following notebooks are available:

0. [Quick start](#0-quick-start)
1. [Keyword, querying, filtering](#1-keyword-querying-filtering)
2. [Hybrid search](#2-hybrid-search)
3. [Semantic search with ELSER](#3-semantic-search-with-elser)

## Notebooks

### 0. Quick start

In  the [`00-quick-start.ipynb`](./00-quick-start.ipynb) notebook you'll learn how to:

- Use the Elasticsearch Python client for various operations.
- Create and define an index for a sample dataset with `dense_vector` fields.
- Transform book titles into embeddings using [Sentence Transformers](https://www.sbert.net) and index them into Elasticsearch.
- Perform k-nearest neighbors (knn) semantic searches.
- Integrate traditional text-based search with semantic search, for a hybrid search system.
- Use reciprocal rank fusion (RRF) to intelligently combine search results from different retrieval systems.

### 1. Keyword, querying, filtering

In the [`01-keyword-querying-filtering.ipynb`](./01-keyword-querying-filtering.ipynb) notebook, you'll learn how to:

- Use [query and filter contexts](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-filter-context.html) to search and filter documents in Elasticsearch.
- Execute full-text searches with `match` and `multi-match` queries.
- Query and filter documents based on `text`, `number`, `date`, or `boolean` values.
- Run multi-field searches using the `multi-match` query.
- Prioritize specific fields in the `multi-match` query for tailored results.


### 2. Hybrid search

In the [`02-hybrid-search.ipynb`](./02-hybrid-search.ipynb) notebook, you'll learn how to:

- Combine results of traditional text-based search with semantic search, for a hybrid search system.
- Transform fields in the sample dataset into embeddings using the Sentence Transformer model and index them into Elasticsearch.
- Use the [RRF API](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html#rrf-api) to combine the results of a `match` query and a `kNN` semantic search.
- Walk through a super simple toy example that demonstrates, step by step, how RRF ranking works.

### 3. Semantic search with ELSER

In the [`03-ELSER.ipynb`](./03-ELSER.ipynb) notebook, you'll learn how to:

- Use the Elastic Learned Sparse Encoder (ELSER) for text expansion-powered semantic search, out of the box — without training, fine-tuning, or embeddings generation.
- Download and deploy the ELSER model in your Elastic environment.
- Create an Elasticsearch index named `search-movies` with specific mappings and index a dataset of movie descriptions.
- Create an ingest pipeline containing an inference processor for ELSER model execution.
- Reindex the data from `search-movies` into another index, `elser-movies`, using the ELSER pipeline for text expansion.
- Observe the results of running the documents through the model by inspecting the additional terms it adds to documents, which enhance searchability.
- Perform simple keyword searches on the `elser-movies` index to assess the impact of ELSER's text expansion.
- Execute ELSER-powered semantic searches using the `text_expansion` query.