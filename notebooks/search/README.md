# Search notebooks

This folder contains a number of notebooks that demonstrate the fundamentals of Elasticsearch, like indexing embeddings, running lexical, semantic and _hybrid_ searches, and more.

The following notebooks are available:

0. [Quick start](#0-quick-start)
1. [Keyword, querying, filtering](#1-keyword-querying-filtering)
2. [Hybrid search](#2-hybrid-search)
3. [Semantic search with ELSER](#3-semantic-search-with-elser)
4. [Multilingual semantic search](#4-multilingual-semantic-search)
5. [Query rules](#5-query-rules)
6. [Synonyms API quick start](#6-synonyms-api-quick-start)

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

### 4. Multilingual semantic search

In the [`04-multilingual.ipynb`](./04-multilingual.ipynb) notebook, you'll learn how to:

- Use a multilingual embedding model for semantic search across languages.
- Transform fields in the sample dataset into embeddings using the Sentence Transformer model and index them into Elasticsearch.
- Use filtering with a `kNN` semantic search.
- Walk through a super simple toy example that demonstrates, step by step, how multilingual search works across languages, and within non-English languages.

### 5. Query rules

In the [`05-query-rules.ipynb`](./05-query-rules.ipynb) notebook, you'll learn how to:

- Use the query rules management APIs to create and edit promotional rules based on contextual queries
- Apply these query rules by using the `rule_query` in Query DSL

### 6. Synonyms API quick start

In the [`06-synonyms-api.ipynb`](./06-synonyms-api.ipynb) notebook, you'll learn how to:

- Use the synonyms management API to create a synonyms set to enhance your search recall
- Configure an index to use search-time synonyms
- Update synonyms in real time
- Run queries that are enhanced by synonyms
