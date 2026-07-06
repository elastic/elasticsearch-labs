"""Elasticsearch helpers for the reference demo.

Handles connection validation, friendly error messages, and Serverless
compatibility (shard settings and refresh are not supported the same way).
"""

from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elastic_transport import ApiError, ConnectionError, ConnectionTimeout
from elasticsearch import AuthenticationException, AuthorizationException

load_dotenv(override=True)

# Settings rejected on Elastic Cloud Serverless (see Elastic docs:
# /docs/reference/elasticsearch/index-settings/serverless)
SERVERLESS_BLOCKED_SETTINGS = frozenset(
    {"number_of_shards", "number_of_replicas"}
)


def require_search_config() -> tuple[str, str, str]:
    """Return (url, api_key, index) or exit with a clear message."""
    url = os.getenv("ELASTICSEARCH_URL", "").strip()
    api_key = os.getenv("ELASTIC_API_KEY", "").strip()
    index = os.getenv("SEARCH_INDEX", "products").strip() or "products"

    missing = []
    if not url:
        missing.append("ELASTICSEARCH_URL")
    if not api_key:
        missing.append("ELASTIC_API_KEY")

    if missing:
        print("Error: Missing required environment variables in .env:")
        for name in missing:
            print(f"  - {name}")
        print("\nCopy .env.example to .env and add your Elastic Cloud credentials.")
        print("See README.md for where to find each value.")
        sys.exit(1)

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        print(f"Error: ELASTICSEARCH_URL is not a valid URL: {url!r}")
        print("Expected format: https://your-deployment.es.region.cloud.es.io")
        sys.exit(1)

    return url, api_key, index


def create_client(url: str, api_key: str) -> Elasticsearch:
    """Build a client with sensible timeouts for setup scripts."""
    return Elasticsearch(
        hosts=[url],
        api_key=api_key,
        request_timeout=30,
        max_retries=2,
        retry_on_timeout=True,
    )


def is_serverless(info: dict[str, Any]) -> bool:
    """Detect Elastic Cloud Serverless from cluster info."""
    return info.get("version", {}).get("build_flavor") == "serverless"


def adapt_mapping_for_cluster(mapping: dict[str, Any], serverless: bool) -> dict[str, Any]:
    """Strip index settings that Serverless does not allow."""
    if not serverless:
        return mapping

    adapted = deepcopy(mapping)
    settings = adapted.get("settings")
    if not isinstance(settings, dict):
        return adapted

    removed = [k for k in SERVERLESS_BLOCKED_SETTINGS if k in settings]
    for key in removed:
        settings.pop(key, None)

    if removed:
        adapted["settings"] = settings

    return adapted


def format_es_error(exc: BaseException) -> str:
    """Turn elasticsearch-py exceptions into actionable messages."""
    if isinstance(exc, AuthenticationException):
        return (
            "Authentication failed (401). Check ELASTIC_API_KEY in .env — "
            "create an API key in Kibana → Stack Management → API Keys."
        )
    if isinstance(exc, AuthorizationException):
        return (
            "Authorization failed (403). This API key may lack index privileges. "
            "Use a key with create_index, index, and read permissions on the cluster."
        )
    if isinstance(exc, ConnectionTimeout):
        return (
            "Connection timed out. Check ELASTICSEARCH_URL points to your deployment "
            "and that the cluster is reachable from this network."
        )
    if isinstance(exc, ConnectionError):
        cause = exc.__cause__
        detail = f" ({cause})" if cause else ""
        return (
            f"Could not connect to Elasticsearch{detail}. "
            "Verify ELASTICSEARCH_URL (host, https, region) and network access."
        )
    if isinstance(exc, ApiError):
        reason = _api_error_reason(exc)
        if reason:
            if "serverless mode" in reason.lower():
                return (
                    f"{reason}\n"
                    "Hint: This project auto-strips shard settings on Serverless. "
                    "If you still see this, update load_data.py or report an issue."
                )
            if "unable to retrieve shard" in reason.lower():
                return (
                    f"{reason}\n"
                    "Hint: Elastic Cloud Serverless does not expose shard APIs. "
                    "Use a stateful Elasticsearch deployment, or ensure you are on "
                    "the latest reference code (refresh/shard settings are skipped)."
                )
            return reason
        return str(exc)

    return str(exc)


def _api_error_reason(exc: ApiError) -> str | None:
    body = exc.body
    if not isinstance(body, dict):
        return None
    err = body.get("error")
    if not isinstance(err, dict):
        return None
    reason = err.get("reason")
    if isinstance(reason, str):
        return reason
    root = err.get("root_cause")
    if isinstance(root, list) and root:
        first = root[0]
        if isinstance(first, dict) and isinstance(first.get("reason"), str):
            return first["reason"]
    return None


def verify_connection(es: Elasticsearch) -> dict[str, Any]:
    """Verify cluster reachability and credentials; return info() or exit with guidance."""
    try:
        return es.info()
    except (AuthenticationException, AuthorizationException, ConnectionError, ConnectionTimeout, ApiError) as exc:
        print(f"Error: {format_es_error(exc)}")
        sys.exit(1)
    except Exception as exc:
        print(f"Error: Unexpected failure connecting to Elasticsearch: {exc}")
        sys.exit(1)


def load_index_mapping(path: str = "index_mapping.json") -> dict[str, Any]:
    """Load index definition from JSON template."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Mapping file not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in {path}: {exc}")
        sys.exit(1)


def ensure_index(
    es: Elasticsearch,
    index: str,
    mapping: dict[str, Any],
    *,
    no_delete: bool,
) -> None:
    """Create or recreate the product index."""
    try:
        exists = es.indices.exists(index=index)
    except (ApiError, ConnectionError, ConnectionTimeout) as exc:
        print(f"Error: Could not check index '{index}': {format_es_error(exc)}")
        sys.exit(1)

    if exists:
        if no_delete:
            print(f"Index '{index}' already exists (keeping existing data)")
            return
        try:
            es.indices.delete(index=index)
            print(f"Deleted existing index '{index}'")
        except ApiError as exc:
            print(f"Error: Could not delete index '{index}': {format_es_error(exc)}")
            sys.exit(1)

    try:
        es.indices.create(
            index=index,
            settings=mapping.get("settings"),
            mappings=mapping.get("mappings"),
        )
        print(f"Created index '{index}'")
    except ApiError as exc:
        print(f"Error: Could not create index '{index}': {format_es_error(exc)}")
        sys.exit(1)


def refresh_index_best_effort(es: Elasticsearch, index: str, serverless: bool) -> None:
    """Refresh index after bulk load; optional on Serverless (near-real-time by default)."""
    if serverless:
        return
    try:
        es.indices.refresh(index=index)
    except ApiError as exc:
        reason = _api_error_reason(exc) or str(exc)
        if "shard" in reason.lower():
            print(f"Note: Skipped refresh (not supported on this deployment): {reason}")
            return
        raise
