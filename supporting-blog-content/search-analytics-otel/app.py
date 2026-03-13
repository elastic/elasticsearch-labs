"""
Search Analytics with OpenTelemetry — Reference Implementation

Accompanies the blog series: "Search Analytics with OTel and Elastic"
  Blog 2 (active):    Search instrumentation with OTel spans
  Blog 3 (commented): Click tracking for CTR and MRR
  Blog 4 (commented): Cart and purchase tracking for conversion funnels

Start with Blog 2 active. Uncomment Blog 3 and 4 sections as you progress.
"""

import json
import os
import time
import threading
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from elasticsearch import Elasticsearch

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor

load_dotenv(override=True)

# =============================================================================
# Configuration
# =============================================================================

ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_API_KEY = os.getenv("ELASTIC_API_KEY")
SEARCH_INDEX = os.getenv("SEARCH_INDEX", "products")
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "search-analytics-demo")
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
OTLP_HEADERS = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")

# Elasticsearch client for search queries
es = Elasticsearch(hosts=[ES_URL], api_key=ES_API_KEY)


# =============================================================================
# OpenTelemetry Setup
# =============================================================================

def _parse_headers(headers_str: str) -> dict:
    """Parse 'Key=Value,Key2=Value2' header format."""
    headers = {}
    for pair in headers_str.split(","):
        pair = pair.strip()
        if "=" in pair:
            key, value = pair.split("=", 1)
            headers[key.strip()] = value.strip()
    return headers


def init_otel(app: FastAPI):
    """Initialize OpenTelemetry with OTLP exporter to Elastic APM."""
    if not OTLP_ENDPOINT:
        print("⚠ OTel disabled: OTEL_EXPORTER_OTLP_ENDPOINT not set")
        return

    resource = Resource.create({
        "service.name": SERVICE_NAME,
        "service.version": "1.0.0",
        "deployment.environment": "development",
    })

    provider = TracerProvider(resource=resource)
    headers = _parse_headers(OTLP_HEADERS)
    # Elastic APM on port 443 expects OTLP/HTTP (not gRPC)
    endpoint = f"{OTLP_ENDPOINT.rstrip('/')}/v1/traces"
    exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Auto-instrument FastAPI and Elasticsearch client
    FastAPIInstrumentor.instrument_app(app)
    ElasticsearchInstrumentor().instrument()

    print(f"✓ OTel enabled: exporting to {OTLP_ENDPOINT}")


tracer = trace.get_tracer("search-api")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(title="Search Analytics Demo")
init_otel(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def index():
    return FileResponse("frontend/index.html")


# ╔══════════════════════════════════════════════════════════════════╗
# ║  BLOG 2: Search Instrumentation (Active)                       ║
# ║                                                                 ║
# ║  This section creates OTel spans with search.* attributes.     ║
# ║  Spans flow to Elastic APM and are queryable via ES|QL.        ║
# ║  See: queries/blog2_search_analytics.esql                      ║
# ╚══════════════════════════════════════════════════════════════════╝

class SearchRequest(BaseModel):
    query: str = ""
    page: int = 1
    page_size: int = 12


@app.post("/api/search")
async def search(request: SearchRequest):
    with tracer.start_as_current_span("search") as span:
        # Generate query_id from trace ID (links searches to clicks)
        query_id = format(span.get_span_context().trace_id, "032x")

        # Set search.* span attributes (see docs/SEMANTIC-CONVENTIONS.md)
        span.set_attribute("search.user_query", request.query.lower().strip())
        span.set_attribute("search.query_id", query_id)
        span.set_attribute("search.application", SERVICE_NAME)
        span.set_attribute("search.page", request.page)
        span.set_attribute("search.page_size", request.page_size)

        # Execute search
        query_body = _build_search_query(
            request.query, request.page, request.page_size
        )
        response = es.search(index=SEARCH_INDEX, body=query_body)

        # Extract results
        hits = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            source["_score"] = hit.get("_score")
            hits.append(source)

        total = response["hits"]["total"]["value"]
        took_ms = response["took"]

        # Record result attributes on span
        span.set_attribute("search.result_count", total)
        span.set_attribute("search.took_ms", took_ms)
        span.set_attribute("search.index", SEARCH_INDEX)
        hit_ids = [h["id"] for h in hits[:20]]
        span.set_attribute("search.query_response_hit_ids", hit_ids)

        return {
            "hits": hits,
            "total": total,
            "took_ms": took_ms,
            "query_id": query_id,
        }


def _build_search_query(query: str, page: int, page_size: int) -> dict:
    """Build Elasticsearch query with BM25 + rank_feature boosting."""
    offset = (page - 1) * page_size

    if not query.strip():
        return {"size": page_size, "from": offset, "query": {"match_all": {}}}

    return {
        "size": page_size,
        "from": offset,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "title^3",
                                "description",
                                "brand^2",
                                "category^1.5",
                            ],
                        }
                    }
                ],
                "should": [
                    {"rank_feature": {"field": "rank_features.popularity", "boost": 2}},
                    {"rank_feature": {"field": "rank_features.margin_score", "boost": 1}},
                    {"rank_feature": {"field": "rank_features.freshness", "boost": 1.5}},
                    {"rank_feature": {"field": "rank_features.conversion_rate", "boost": 1}},
                ],
            }
        },
        "_source": [
            "id", "title", "description", "category", "brand",
            "price", "rating", "review_count", "in_stock", "image_url",
        ],
    }


# ╔══════════════════════════════════════════════════════════════════╗
# ║  BLOG 3: Click Tracking                                        ║
# ║                                                                 ║
# ║  Uncomment this section to enable click tracking.               ║
# ║  Then restart the server and run:                               ║
# ║    python generate_traffic.py --blog 3 --sessions 50           ║
# ║  See: queries/blog3_click_quality.esql                         ║
# ╚══════════════════════════════════════════════════════════════════╝

# # --- First-click tracking (for CTR calculation) ---
# _clicked_queries: dict[str, float] = {}  # query_id -> timestamp
# _clicked_queries_lock = threading.Lock()
#
#
# def _is_first_click(query_id: str) -> bool:
#     """Check if this is the first click for a given query_id."""
#     now = time.time()
#     with _clicked_queries_lock:
#         # Prune entries older than 30 minutes
#         cutoff = now - 1800
#         expired = [k for k, v in _clicked_queries.items() if v < cutoff]
#         for k in expired:
#             del _clicked_queries[k]
#         if query_id in _clicked_queries:
#             return False
#         _clicked_queries[query_id] = now
#         return True
#
#
# class ClickEvent(BaseModel):
#     object_id: str = Field(..., description="Product ID clicked")
#     position: int = Field(..., ge=1, description="Position in results (1-based)")
#     query_id: Optional[str] = None
#     client_id: Optional[str] = None
#     user_query: Optional[str] = None
#
#
# @app.post("/api/events")
# async def track_click(event: ClickEvent):
#     """Record a search result click as an OTel span."""
#     with tracer.start_as_current_span("search.result.click") as span:
#         span.set_attribute("search.action", "click")
#         span.set_attribute("search.result_click_id", event.object_id)
#         span.set_attribute("search.result_click_position", event.position)
#
#         if event.query_id:
#             span.set_attribute("search.query_id", event.query_id)
#         if event.client_id:
#             span.set_attribute("search.client_id", event.client_id)
#         if event.user_query:
#             span.set_attribute("search.user_query", event.user_query.lower().strip())
#
#         # First-click flag enables single-query CTR calculation
#         if event.query_id and _is_first_click(event.query_id):
#             span.set_attribute("search.first_click", True)
#
#         return {"status": "ok", "query_id": event.query_id}


# ╔══════════════════════════════════════════════════════════════════╗
# ║  BLOG 4: Conversion Tracking                                   ║
# ║                                                                 ║
# ║  Uncomment this section to enable cart and purchase tracking.   ║
# ║  Requires: Blog 3 must be uncommented first.                   ║
# ║  Then restart the server and run:                               ║
# ║    python generate_traffic.py --blog 4 --sessions 100          ║
# ║  See: queries/blog4_conversions.esql                           ║
# ╚══════════════════════════════════════════════════════════════════╝

# class CartEvent(BaseModel):
#     object_id: str = Field(..., description="Product ID added to cart")
#     position: int = Field(..., ge=1, description="Position in results (1-based)")
#     query_id: Optional[str] = None
#     client_id: Optional[str] = None
#     user_query: Optional[str] = None
#     quantity: int = 1
#     price: Optional[float] = None
#
#
# @app.post("/api/cart/add")
# async def add_to_cart(event: CartEvent):
#     """Record an add-to-cart event as an OTel span."""
#     with tracer.start_as_current_span("cart.add") as span:
#         span.set_attribute("search.action", "add_to_cart")
#         span.set_attribute("search.result_click_id", event.object_id)
#         span.set_attribute("search.result_click_position", event.position)
#         span.set_attribute("cart.quantity", event.quantity)
#
#         if event.price is not None:
#             span.set_attribute("cart.price", event.price)
#         if event.query_id:
#             span.set_attribute("search.query_id", event.query_id)
#         if event.client_id:
#             span.set_attribute("search.client_id", event.client_id)
#         if event.user_query:
#             span.set_attribute("search.user_query", event.user_query.lower().strip())
#
#         return {"status": "ok"}
#
#
# class CheckoutItem(BaseModel):
#     object_id: str
#     quantity: int = 1
#     price: float
#
#
# class CheckoutEvent(BaseModel):
#     order_id: str
#     total_amount: float
#     items: List[CheckoutItem] = []
#     client_id: Optional[str] = None
#     query_id: Optional[str] = None
#     user_query: Optional[str] = None
#
#
# @app.post("/api/checkout")
# async def checkout(event: CheckoutEvent):
#     """Record a purchase as an OTel span."""
#     with tracer.start_as_current_span("checkout.complete") as span:
#         span.set_attribute("search.action", "purchase")
#         span.set_attribute("checkout.order_id", event.order_id)
#         span.set_attribute("checkout.total_amount", event.total_amount)
#         span.set_attribute("checkout.item_count", len(event.items))
#
#         if event.client_id:
#             span.set_attribute("search.client_id", event.client_id)
#         if event.query_id:
#             span.set_attribute("search.query_id", event.query_id)
#         if event.user_query:
#             span.set_attribute("search.user_query", event.user_query.lower().strip())
#
#         return {"status": "ok", "order_id": event.order_id}


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    print(f"\n  Search Analytics Demo: http://localhost:{port}\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
