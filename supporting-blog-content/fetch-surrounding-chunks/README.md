# Fetch Surrounding Chunks (N-1, N+1)

This notebook is designed to handle the ingestion of book text (Harry Potter and the Sorcerer's Stone) into an Elasticsearch Cloud instance. It includes partitioning the book text into chapters and chunking the chapter text, which are then ingested into Elasticsearch. The setup utilizes a nested structure, and for each chunk, it stores dense and sparse (ELSER) vector representations along with the text representation.

Searches are performed using dense vector comparisons, sparse vector comparisons, and text search in parallel to demonstrate the power of hybrid search strategies. Additionally, the notebook is configured to retrieve adjacent chunks (n-1 and n+1), allowing for a more contextual understanding of the search results.

## Elasticsearch Version
Versions of Elasticsearch `8.13` and `8.14` were tested with this notebook.  The notebook will not work with previous versions Elasticsearch
