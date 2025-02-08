import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

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

def process_evidence(generator, es_manager, file_path, modality, description, metadata):
    """Helper function to process each piece of evidence"""
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return

        embedding = generator.generate_embedding([file_path], modality)
        response = es_manager.index_content(
            embedding=embedding,
            modality=modality,
            description=description,
            content_path=file_path,
            metadata=metadata
        )
        
        # Convert Elasticsearch response to dict for JSON serialization
        response_dict = {
            "result": response["result"],
            "_id": response["_id"],
            "_index": response["_index"]
        }
        logger.info(f"\n\nIndexed {modality}: {json.dumps(response_dict, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error processing {modality}: {str(e)}")

def main():
    # Initialize components
    generator = EmbeddingGenerator()
    es_manager = ElasticsearchManager()

    # Create data directories if they don't exist
    for dir_name in ["images", "audios", "texts", "depths"]:
        os.makedirs(os.path.join("data", dir_name), exist_ok=True)

    # List of evidence to process
    evidence_list = [
        {
            "file_path": "data/images/crime_scene1.jpg",
            "modality": "vision",
            "description": "Photo of the crime scene: A dark, rain-soaked alley is filled with playing cards, while a sinister graffiti of the Joker laughing stands out on the brick wall.",
            "metadata": {"location": "Gotham Central Bank", "timestamp": "2025-01-30 23:15"}
        },
        {
            "file_path": "data/images/joker_laughing.png",
            "modality": "vision",
            "description": "The Joker with green hair, white face paint, and a sinister smile in an urban night setting.",
            "metadata": {"location": "Gotham Theatre", "timestamp": "2025-01-30 23:25"}
        },
        {
            "file_path": "data/images/jdancing.png",
            "modality": "vision",
            "description": "Suspect dancing",
            "metadata": {"location": "Gotham Central Station", "timestamp": "2025-01-30 23:18"}
        },
        {
            "file_path": "data/audios/joker_laugh.wav",
            "modality": "audio",
            "description": "A sinister laugh captured near the crime scene",
            "metadata": {"location": "Gotham Central Bank - Main Hall", "timestamp": "2025-01-30 23:16"}
        },
        {
            "file_path": "data/texts/note2.txt",
            "modality": "text",
            "description": "Why so serious",
            "metadata": {"location": "Gotham Theatre", "timestamp": "2025-01-30 23:25"}
        },
        {
            "file_path": "data/texts/riddle.txt",
            "modality": "text",
            "description": "Mysterious note found at the location",
            "metadata": {"location": "Gotham Central Bank - Vault", "timestamp": "2025-01-30 23:20"}
        },
        {
            "file_path": "data/depths/depth_suspect.png",
            "modality": "depth",
            "description": "Depth sensor capture of the suspect",
            "metadata": {"location": "Gotham Central Bank - Back Alley", "timestamp": "2025-01-30 23:18"}
        }
    ]

    # Process each piece of evidence
    for evidence in evidence_list:
        process_evidence(
            generator,
            es_manager,
            evidence["file_path"],
            evidence["modality"],
            evidence["description"],
            evidence["metadata"]
        )

if __name__ == "__main__":
    main()