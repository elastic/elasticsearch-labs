# Elasticsearch LLM Cache
A Python library to utilize Elasticsearch as a caching layer for Generative AI applications. By caching the responses from Language Models (LLMs), this library helps in reducing costs associated with LLM services and improving response speed from the user's perspective.

# Blog Post
This library is covered in depth in the blog post [Elasticsearch as a GenAI Caching Layer](https://www.elastic.co/search-labs/elasticsearch-as-a-genai-caching-layer).

## Key Benefits
- Reduce costs for LLM services by reusing previous responses.
- Improve response speed as seen by end users by serving cached responses.

## Class: `ElasticsearchLLMCache`
This class provides the core functionality for creating, querying, and updating a cache index in Elasticsearch.

### `__init__(self, es_client: Elasticsearch, index_name: Optional[str] = None, es_model_id: Optional[str] = 'sentence-transformers__all-distilroberta-v1', create_index=True)`
Constructor method to initialize the ElasticsearchLLMCache instance.

- `es_client` (Elasticsearch): Elasticsearch client object.
- `index_name` (str, optional): Name for the index; defaults to 'llm_cache'.
- `es_model_id` (str, optional): Model ID for text embedding; defaults to 'sentence-transformers__all-distilroberta-v1'.
- `create_index` (bool, optional): Whether to create a new index; defaults to True.

### `create_index(self, dims: Optional[int] = 768) -> Dict`
Method to create a new index for caching if it does not already exist.

- `dims` (int, optional): The dimensionality of the vector; defaults to 768.

**Returns**:
- Dictionary containing information about index creation.

**Mapping**:
- `prompt`: text
- `response`: text
- `create_date`: date
- `last_hit_date`: date
- `prompt_vector`: dense_vector

### `query(self, prompt_text: str, similarity_threshold: Optional[float] = 0.5) -> dict`
Method to query the index to find similar prompts and update the `last_hit_date` for that document if a hit is found.

- `prompt_text` (str): The text of the prompt to find similar entries for.
- `similarity_threshold` (float, optional): The similarity threshold for filtering results; defaults to 0.5.

**Returns**:
- A dictionary containing the hits or an empty dictionary if no hits are found.

### `add(self, prompt: str, response: str, source: Optional[str] = None) -> dict`
Method to add a new document to the index when there is no cache hit and a response is fetched from LLM.

- `prompt` (str): The user prompt.
- `response` (str): The LLM response.
- `source` (str, optional): Source identifier for the LLM.

**Returns**:
- A dictionary indicating the successful caching of the new prompt and response.

## Example Usage
```python
from elasticsearch import Elasticsearch
from elasticsearch_llm_cache import ElasticsearchLLMCache

# Initialize Elasticsearch client
es_client = Elasticsearch()

# Initialize Elasticsearch LLM Cache
llm_cache = ElasticsearchLLMCache(es_client)

# Query the cache
cache_response = llm_cache.query(prompt_text="Hello, how can I help?")

# If no cache hit, add new response to cache
if not cache_response:
    llm_response = "I'm here to assist you!"  # Assume this response is fetched from LLM
    llm_cache.add(prompt="Hello, how can I help?", response=llm_response)
   ```

# Example Files
## [elasticRAG_with_cache.py](elasticRAG_with_cache.py)
Sample Streamlit App using RAG with Elasticsearch

- uses existing ElasticSearch Elastic Cloud Deployment
- uses either OpenAI or Azure OpenAI for GenAI
  - can be modified to work with any GenAI service
- Environment Variables
  - OPENAI_API_TYPE
  - OPENAI_API_BASE
  - OPENAI_API_VERSION
  - OPENAI_API_ENGINE
  - ELASTIC_APM_SERVICE_NAME
  - ELASTIC_CLOUD_ID
  - ELASTIC_USER
  - ELASTIC_PASSWORD
  - ELASTIC_INDEX_DOCS

## [test_elasticsearch_llm_cache.py](test_elasticsearch_llm_cache.py)
Unit tests for ElasticsearchLLMCache class
