<img src="https://github.com/user-attachments/assets/b2879240-ae16-4544-ae67-3d261a67e2a1" width="50%"/>

## Elastic Book Search
This is a companion codebase for the article *Navigating an Elastic Vector Database* found [Navigating an Elastic Vector Database](). This contains all of the necessary instructions to create and operate a vector database with Elasticsearch.

Folder contents:

### `example.env`
Update and rename this file to only `.env`. Provide your own credentials for the Elasticsearch Endpoint and Elastic API Key. The default index name for this repository is set to `books`

### `src/`

#### `src/elastic_client.py`: connector to Elasticsearch. Draws credentials from the above `.env` file.

#### `src/upload_books_local_embed.py`: scripts to upload books to Elasticsearch with local embedding.
  This file will run an embedding model locally to create vectors for each book object. The new books list with vectors will then be indexed into Elasticsearch.

  - **Functions**:
    - `embed_descriptions()`: Converts the `book_description` field into a vector.
    - `create_index()`: Creates the Elasticsearch index `books-local` for storing book documents.
    - `bulk_upload()`: Uploads multiple book documents to the Elasticsearch index in bulk.
    - `upload_single_book()`: Uploads a single book document to the Elasticsearch index.

  - **How to run**:
  1. Ensure Elasticsearch is running locally.
  2. Navigate to the `src/` directory.
  3. Run the script using Python:
      ```sh
      python upload_books_local_embed.py
      ```
  4. By default the script will run a small batch of books (25) for faster performance. Embedding and indexing the full `books.json` will take longer, but the search results will be more relevant. 

#### `src/upload_books_with_pipeline.py`: scripts to upload books to Elasticsearch with ingestion pipeline functionality.
  This file will create an inference ingestion pipeline to instruct Elasticsearch to create a vector embedding of all `book_description` fields that are indexed. This moves the embedding computation from the local machine to the Elasticsearch instance.  

  Note: you will need to upload and deploy the embedding model to Elasticsearch via the execution of a Docker image. Full instructions are available [here](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-text-emb-vector-search-example.html).
  
- **Functions**:
  - `create_ingest_pipeline()`: Creates an inference ingestion pipeline to embed vectors when documents are indexed.
  - `create_index()`: Creates the Elasticsearch index `books-pipeline` for storing book documents.
  - `bulk_upload()`: Uploads multiple book documents to the Elasticsearch index in bulk.
  - `upload_single_book()`: Uploads a single book document to the Elasticsearch index.

- **How to run**:
1. Ensure Elasticsearch is running locally.
2. Navigate to the `src/` directory.
3. Run the script using Python:
    ```sh
    python upload_books_with_pipeline.py
    ```
4. By default the script will run all books (10,908) as all embedding occurs on the Elasticsearch instance.


#### `src/query_examples.py`: scripts to demonstrate various query examples for searching books in Elasticsearch.
  This file contains three different types of search examples: traditional (bm25), vector, and hybrid search. Hybrid utilizes both search types then combines the results in a normalized ranking order.

  - **Functions**:
    - `vector_search()`: performs a vector search with a given query string.
    - `search()`: performs a traditional search.
    - `hybrid_search(q)`: performs a hybrid search.


  - **How to run**:
  1. Ensure Elasticsearch is running locally.
  2. Navigate to the `src/` directory.
  3. Run the script using Python:
      ```sh
      python query_examples.py
      ```
  4. Modify the query parameters within the script to test different search criteria and observe the results.

### `notebooks/`
Python notebooks have been provided of the above python scripts for more interactivity.
