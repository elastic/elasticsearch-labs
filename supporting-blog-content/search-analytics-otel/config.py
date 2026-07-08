"""Application configuration loaded from .env.

Tutorial focus: Elasticsearch credentials for the product index.
OpenTelemetry export is configured via standard OTEL_* env vars (see otel_setup.py).
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv(override=True)

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "").strip()
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY", "").strip()
SEARCH_INDEX = os.getenv("SEARCH_INDEX", "products").strip() or "products"
PORT = int(os.getenv("PORT", "8000"))


def require_elasticsearch_config() -> None:
    """Exit with a helpful message if search cluster credentials are missing."""
    missing = []
    if not ELASTICSEARCH_URL:
        missing.append("ELASTICSEARCH_URL")
    if not ELASTIC_API_KEY:
        missing.append("ELASTIC_API_KEY")

    if missing:
        print("Error: Missing required environment variables in .env:")
        for name in missing:
            print(f"  - {name}")
        print("\nCopy .env.example to .env and add your Elastic Cloud credentials.")
        sys.exit(1)
