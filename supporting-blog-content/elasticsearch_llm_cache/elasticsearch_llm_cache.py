"""
Elasticsearch LLM Cache Library
==================================
This library provides an Elasticsearch-based caching mechanism for Language Model (LLM) responses.
Through the ElasticsearchLLMCache class, it facilitates the creation, querying, and updating
of a cache index to store and retrieve LLM responses based on user prompts.

Key Features:
-------------
- Initialize a cache index with specified or default settings.
- Create the cache index with specified mappings if it does not already exist.
- Query the cache for similar prompts using a k-NN (k-Nearest Neighbors) search.
- Update the 'last_hit_date' field of a document when a cache hit occurs.
- Generate a vector for a given prompt using Elasticsearch's text embedding.
- Add new documents (prompts and responses) to the cache.

Requirements:
-------------
- Elasticsearch
- Python 3.6+
- elasticsearch-py library

Usage Example:
--------------
```python
from elasticsearch import Elasticsearch
from elasticsearch_llm_cache import ElasticsearchLLMCache

# Initialize Elasticsearch client
es_client = Elasticsearch()

# Initialize the ElasticsearchLLMCache instance
llm_cache = ElasticsearchLLMCache(es_client)

# Query the cache
prompt_text = "What is the capital of France?"
query_result = llm_cache.query(prompt_text)

# Add to cache
prompt = "What is the capital of France?"
response = "Paris"
add_result = llm_cache.add(prompt, response)
```

This library is covered in depth in the blog post
Elasticsearch as a GenAI Caching Layer
https://www.elastic.co/blog/lasticsearch-as-a-genai-caching-layer

Author: Jeff Vestal
Version: 1.0.0

"""

from datetime import datetime
from typing import Dict, List, Optional
from elasticsearch import Elasticsearch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElasticsearchLLMCache:
    def __init__(self,
                 es_client: Elasticsearch,
                 index_name: Optional[str] = None,
                 es_model_id: Optional[str] = 'sentence-transformers__all-distilroberta-v1',
                 create_index=True
                 ):
        """
        Initialize the ElasticsearchLLMCache instance.

        :param es_client: Elasticsearch client object.
        :param index_name: Optional name for the index; defaults to 'llm_cache'.
        :param es_model_id: Model ID for text embedding; defaults to 'sentence-transformers__all-distilroberta-v1'.
        :param create_index: Boolean to determine whether to create a new index; defaults to True.
        """
        self.es = es_client
        self.index_name = index_name or 'llm_cache'
        self.es_model_id = es_model_id
        if create_index:
            self.create_index()

    def create_index(self,
                     dims: Optional[int] = 768
                     ) -> Dict:
        """
        Create the index if it does not already exist.

        :return: Dictionary containing information about the index creation.
        """
        if not self.es.indices.exists(index=self.index_name):
            mappings = {
                "mappings": {
                    "properties": {
                        "prompt": {"type": "text"},
                        "response": {"type": "text"},
                        "create_date": {"type": "date"},
                        "last_hit_date": {"type": "date"},
                        "prompt_vector": {"type": "dense_vector",
                                          "dims": dims,
                                          "index": True,
                                          "similarity": "dot_product"
                                          }
                    }
                }
            }

            self.es.indices.create(index=self.index_name, body=mappings, ignore=400)
            logger.info(f"Index {self.index_name} created.")

            return {'cache_index': self.index_name, 'created_new': True}
        else:
            logger.info(f"Index {self.index_name} already exists.")
            return {'cache_index': self.index_name, 'created_new': False}

    def update_last_hit_date(self, doc_id: str):
        """
        Update the 'last_hit_date' field of a document to the current datetime.

        :param doc_id: The ID of the document to update.
        """
        update_body = {
            "doc": {
                "last_hit_date": datetime.now()
            }
        }
        self.es.update(index=self.index_name, id=doc_id, body=update_body)

    def query(self,
              prompt_text: str,
              similarity_threshold: Optional[float] = 0.5
              ) -> dict:
        """
        Query the index to find similar prompts and update the `last_hit_date` for that document if a hit is found.

        :param prompt_text: The text of the prompt to find similar entries for.
        :param similarity_threshold: The similarity threshold for filtering results; defaults to 0.5.
        :return: A dictionary containing the hits or an empty dictionary if no hits are found.
        """
        knn = [
            {
                "field": "prompt_vector",
                "k": 1,
                "num_candidates": 1000,
                "similarity": similarity_threshold,
                "query_vector_builder": {
                    "text_embedding": {
                        "model_id": self.es_model_id,
                        "model_text": prompt_text
                    }
                }
            }
        ]

        fields = [
            "prompt",
            "response"
        ]

        resp = self.es.search(index=self.index_name,
                              knn=knn,
                              fields=fields,
                              size=1,
                              source=False
                              )

        if resp['hits']['total']['value'] == 0:
            return {}
        else:
            doc_id = resp['hits']['hits'][0]['_id']
            self.update_last_hit_date(doc_id)
            return resp['hits']['hits'][0]['fields']

    def _generate_vector(self,
                         prompt: str
                         ) -> List[float]:
        """
        Generate a vector for a given prompt using Elasticsearch's text embedding.

        :param prompt: The text prompt to generate a vector for.
        :return: A list of floats representing the vector.
        """
        docs = [
            {
                "text_field": prompt
            }
        ]

        embedding = self.es.ml.infer_trained_model(model_id=self.es_model_id,
                                                   docs=docs
                                                   )

        return embedding['inference_results'][0]['predicted_value']

    def add(self, prompt: str,
            response: str,
            source: Optional[str] = None
            ) -> dict:
        """
        Add a new document to the index.

        :param prompt: The user prompt.
        :param response: The LLM response.
        :param source: Optional source identifier for the LLM.
        :return: A dictionary indicating the successful caching of the new prompt and response.
        """
        prompt_vector = self._generate_vector(prompt=prompt)

        doc = {
            "prompt": prompt,
            "response": response,
            "create_date": datetime.now(),
            "last_hit_date": datetime.now(),
            "prompt_vector": prompt_vector,
            "source": source  # Optional
        }
        self.es.index(index=self.index_name, document=doc)
        return {'success caching new prompt & response': True}
