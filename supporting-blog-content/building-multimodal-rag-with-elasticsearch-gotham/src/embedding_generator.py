import base64
import logging
import mimetypes
import os

import numpy as np
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ApiError, NotFoundError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_MODEL_ID = "jina-embeddings-v5-omni-small"
DEFAULT_INFERENCE_ID = "jina-embeddings-v5-omni-small"


class EmbeddingGenerator:
    """Generates multimodal embeddings using Elasticsearch inference."""

    def __init__(self):
        load_dotenv()
        self.es = self._connect_elasticsearch()
        self.inference_id = DEFAULT_INFERENCE_ID
        self.model_id = DEFAULT_MODEL_ID
        self._ensure_inference_endpoint()

    def _connect_elasticsearch(self):
        """Connects to Elasticsearch."""
        elasticsearch_url = os.getenv("ELASTICSEARCH_URL")
        elasticsearch_user = os.getenv("ELASTICSEARCH_USER")
        elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")
        elasticsearch_api_key = os.getenv("ELASTICSEARCH_API_KEY")

        if not elasticsearch_url:
            raise ValueError("ELASTICSEARCH_URL must be set in your .env file")

        if elasticsearch_user:
            return Elasticsearch(
                hosts=[elasticsearch_url],
                basic_auth=(elasticsearch_user, elasticsearch_password),
            )
        if elasticsearch_api_key:
            return Elasticsearch(hosts=[elasticsearch_url], api_key=elasticsearch_api_key)
        raise ValueError(
            "Please set ELASTICSEARCH_API_KEY or ELASTICSEARCH_USER/ELASTICSEARCH_PASSWORD"
        )

    def _ensure_inference_endpoint(self):
        try:
            self.es.inference.get(task_type="embedding", inference_id=self.inference_id)
            return
        except NotFoundError:
            pass
        except ApiError as err:
            if getattr(err, "meta", None) and err.meta.status == 404:
                pass
            else:
                raise

        # Create the inference endpoint if it does not exist
        self.es.inference.put(
            task_type="embedding",
            inference_id=self.inference_id,
            body={
                "service": "elastic",
                "service_settings": {"model_id": self.model_id},
            },
            timeout="120s",
        )

    def generate_embedding(self, input_data, modality):
        """Generates one embedding for a single text/image/audio input."""
        if modality not in {"vision", "audio", "text"}:
            raise ValueError(f"Unsupported modality: {modality}")
        if not isinstance(input_data, list) or len(input_data) != 1:
            raise ValueError("input_data must be a list with a single item")

        input_payload = self._build_input_payload(input_data[0], modality)
        response = self.es.inference.embedding(
            inference_id=self.inference_id,
            embedding={
                "input": input_payload,
                "input_type": "search",
            },
        )

        embeddings = response.get("embeddings") or response.get("data") or []
        if not embeddings:
            raise ValueError("No embeddings returned by inference API")
        first_embedding = embeddings[0].get("embedding")
        if first_embedding is None:
            raise ValueError("Embedding field not found in inference response")
        return np.array(first_embedding, dtype=np.float32)

    def _build_input_payload(self, value, modality):
        if modality == "text":
            return [
                {
                    "content": {
                        "type": "text",
                        "format": "text",
                        "value": value,
                    }
                }
            ]

        if not os.path.exists(value):
            raise FileNotFoundError(f"Input file not found: {value}")

        content_type = "image" if modality == "vision" else "audio"
        mime_type = mimetypes.guess_type(value)[0]
        if not mime_type:
            mime_type = "image/jpeg" if modality == "vision" else "audio/wav"

        with open(value, "rb") as file:
            encoded = base64.b64encode(file.read()).decode("utf-8")

        return [
            {
                "content": {
                    "type": content_type,
                    "format": "base64",
                    "value": f"data:{mime_type};base64,{encoded}",
                }
            }
        ]
