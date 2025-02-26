import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src")
)

from embedding_generator import EmbeddingGenerator
from elastic_manager import ElasticsearchManager
import json
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize classes
generator = EmbeddingGenerator()
es_manager = ElasticsearchManager()

# Generate embedding for a suspicious depth map
vision_embedding = generator.generate_embedding(
    ["data/depths/jdancing-depth.png"], "depth"
)

# Search for similar evidence in Elasticsearch
similar_evidences = es_manager.search_similar(
    query_embedding=vision_embedding, modality="vision", k=3
)

# Display the retrieved results
print("\n🔎 Similar evidence found:\n")
for i, evidence in enumerate(similar_evidences, start=1):
    description = evidence["description"]
    modality = evidence["modality"]
    score = evidence["score"]
    content_path = evidence.get("content_path", "N/A")

    print(f"{i}. {description} ({modality})")
    print(f"   Similarity: {score:.4f}")
    print(f"   File path: {content_path}\n")
