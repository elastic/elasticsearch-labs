from elasticsearch import Elasticsearch, helpers
import base64
import os
from dotenv import load_dotenv
import numpy as np


class ElasticsearchManager:
    """Manages multimodal operations in Elasticsearch"""

    def __init__(self):
        load_dotenv()  # Load variables from .env
        self.es = self._connect_elastic()
        self.index_name = "multimodal_content"
        self._setup_index()

    def _connect_elastic(self):
        """Connects to Elasticsearch"""
        ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
        ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER")
        ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
        ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")

        if ELASTICSEARCH_USER:
            return Elasticsearch(
                hosts=[ELASTICSEARCH_URL],
                basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
            )
        elif ELASTICSEARCH_API_KEY:
            return Elasticsearch(
                hosts=[ELASTICSEARCH_URL], api_key=ELASTICSEARCH_API_KEY
            )
        else:
            raise ValueError(
                "Please provide either ELASTICSEARCH_USER or ELASTICSEARCH_API_KEY"
            )

    def _setup_index(self):
        """Sets up the index if it doesn't exist"""
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 1024,
                            "index": True,
                            "similarity": "cosine",
                        },
                        "modality": {"type": "keyword"},
                        "content": {"type": "binary"},
                        "description": {"type": "text"},
                        "metadata": {"type": "object"},
                        "content_path": {"type": "text"},
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=mapping)

    def index_content(
        self,
        embedding,
        modality,
        content=None,
        description="",
        metadata=None,
        content_path=None,
    ):
        """Indexes multimodal content"""
        doc = {
            "embedding": embedding.tolist(),
            "modality": modality,
            "description": description,
            "metadata": metadata or {},
            "content_path": content_path,
        }

        if content:
            doc["content"] = (
                base64.b64encode(content).decode()
                if isinstance(content, bytes)
                else content
            )

        return self.es.index(index=self.index_name, document=doc)

    def search_similar(self, query_embedding, modality=None, k=5):
        """Searches for similar contents"""
        query = {
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding.tolist(),
                "k": k,
                "num_candidates": 100,
                "filter": [{"term": {"modality": modality}}] if modality else [],
            }
        }

        try:
            response = self.es.search(index=self.index_name, query=query, size=k)

            # Return both source data and score for each hit
            return [
                {**hit["_source"], "score": hit["_score"]}
                for hit in response["hits"]["hits"]
            ]

        except Exception as e:
            print(f"Error: processing search_evidence: {str(e)}")
            return "Error generating search evidence"
