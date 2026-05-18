import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src")
)

from elastic_manager import ElasticsearchManager
from llm_analyzer import LLMAnalyzer

import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize classes
es_manager = ElasticsearchManager()

llm = LLMAnalyzer()
logger.info("✅ All components initialized successfully")

try:
    evidence_data = {}

    # Get data for each modality
    test_files = {
        "vision": "data/images/crime_scene2.jpg",
        "audio": "data/audios/joker_laugh.wav",
        "text": "Why so serious?",
    }

    logger.info("🔍 Collecting evidence...")
    for modality, test_input in test_files.items():
        try:
            results = es_manager.search_similar(query_input=test_input, k=2)
            if results:
                evidence_data[modality] = results
                logger.info(f"✅ Data retrieved for {modality}: {len(results)} results")
            else:
                logger.warning(f"⚠️ No results found for {modality}")

        except Exception as e:
            logger.error(f"❌ Error retrieving {modality} data: {str(e)}")

    if not evidence_data:
        raise ValueError("No evidence data found in Elasticsearch!")

    # Test forensic report generation
    logger.info("\n📝 Generating forensic report...")
    report = llm.analyze_evidence(evidence_data)

    if report:
        logger.info("✅ Forensic report generated successfully")
        logger.info("\n📊 Report Preview:")
        logger.info("+" * 50)
        logger.info(report)
        logger.info("+" * 50)
    else:
        raise ValueError("Failed to generate forensic report")

except Exception as e:
    logger.error(f"❌ Error in analysis : {str(e)}")
