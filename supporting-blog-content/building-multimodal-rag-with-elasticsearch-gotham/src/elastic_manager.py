from elasticsearch import Elasticsearch
import base64
import os
from dotenv import load_dotenv


class ElasticsearchManager:
    """Manages multimodal operations in Elasticsearch"""

    def __init__(self):
        self.es = self.connect_elastic()
        self.index_name = "multimodal_content"
        self.inference_id = ".jina-embeddings-v5-omni-small"
        self._setup_index()

    @staticmethod
    def connect_elastic():
        """Connects to Elasticsearch."""
        load_dotenv()  # Load variables from .env
        ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
        ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER")
        ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
        ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
        client_config = {
            "hosts": [ELASTICSEARCH_URL],
            "request_timeout": 60,
            "max_retries": 3,
            "retry_on_timeout": True,
        }

        if ELASTICSEARCH_USER:
            return Elasticsearch(
                **client_config,
                basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
            )
        elif ELASTICSEARCH_API_KEY:
            return Elasticsearch(**client_config, api_key=ELASTICSEARCH_API_KEY)
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
                        "content": {
                            "type": "semantic_text",
                            "inference_id": self.inference_id,
                        },
                        "modality": {"type": "keyword"},
                        "description": {"type": "text"},
                        "metadata": {"type": "object"},
                        "content_path": {"type": "text"},
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=mapping)
            return

    def index_content(
        self,
        modality,
        content,
        description="",
        metadata=None,
        content_path=None,
    ):
        """Indexes multimodal content"""
        doc = {
            "content": content,
            "modality": modality,
            "description": description,
            "metadata": metadata or {},
            "content_path": content_path,
        }

        return self.es.index(index=self.index_name, document=doc)

    def search_similar(self, query_input, k=5):
        """Searches for similar contents"""
        query = {
            "semantic": {
                "field": "content", 
                "query": query_input
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

    def build_content_from_file(self, file_path, modality):
        """Converts image/audio/video files into base64 data URIs."""
        mime_types = {
            "vision": "image/jpeg",
            "audio": "audio/wav",
            "video": "video/mp4",
        }

        with open(file_path, "rb") as file:
            encoded = base64.b64encode(file.read()).decode("utf-8")

        mime_type = mime_types[modality]
        return f"data:{mime_type};base64,{encoded}"
