import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src")
)

from elastic_manager import ElasticsearchManager
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize class
es_manager = ElasticsearchManager()

# Search using the audio file itself as the semantic query
audio_query_path = "data/audios/joker_laugh.wav"
query_content = es_manager.build_content_from_file(
    audio_query_path, "audio"
)
print(f"\n🧾 Query used for search:\n{audio_query_path}\n")
similar_evidences = es_manager.search_similar(query_input=query_content, k=3)

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
