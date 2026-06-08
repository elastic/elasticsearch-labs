"""
Search Analytics with OpenTelemetry — Reference Implementation

Blog series: "Search Analytics with OTel and Elastic"

  Blog 2 (active):    Search spans with search.* attributes
  Blog 3 (active):    Click tracking (CTR, MRR)
  Blog 4 (active):    Cart and purchase funnel

Files:
  app.py           — API routes and span attributes (tutorial focus)
  otel_setup.py    — EDOT bootstrap / .env fixes (skim if you like)
  config.py        — Elasticsearch connection from .env
  search_queries.py — Elasticsearch query JSON
  load_data.py     — Index sample products
"""

from typing import List, Optional  # used when Blog 3/4 sections are uncommented

from elasticsearch import Elasticsearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field  # Field used by Blog 3/4 models

import config
from otel_setup import init_otel
from search_queries import build_product_search

# -----------------------------------------------------------------------------
# Elasticsearch client (product catalog)
# -----------------------------------------------------------------------------

config.require_elasticsearch_config()

es = Elasticsearch(
    hosts=[config.ELASTICSEARCH_URL],
    api_key=config.ELASTIC_API_KEY,
)

# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------

app = FastAPI(title="Search Analytics Demo")

# One-line OTel setup — details in otel_setup.py
tracer = init_otel(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def index():
    return FileResponse("frontend/index.html")


# =============================================================================
# BLOG 2: Search instrumentation (active)
#
# Every POST /api/search creates a span named "search" with:
#   - search.*     custom attributes for ES|QL analytics
#   - trace_id     exposed as search.query_id (ties clicks/purchases later)
#
# Data lands in traces-generic.otel-default when exporting to managed OTLP.
# Example queries: queries/blog2_search_analytics.esql
# =============================================================================


class SearchRequest(BaseModel):
    query: str = ""
    page: int = 1
    page_size: int = 12


@app.post("/api/search")
async def search(request: SearchRequest):
    # --- Create the span readers will query in Kibana / ES|QL ---
    with tracer.start_as_current_span("search") as span:
        # Correlate this search with later click/cart events (Blogs 3–4)
        query_id = format(span.get_span_context().trace_id, "032x")

        # What the user searched for
        normalized_query = request.query.lower().strip()
        span.set_attribute("search.query", normalized_query)
        span.set_attribute("search.query_id", query_id)
        span.set_attribute("search.page", request.page)
        span.set_attribute("search.page_size", request.page_size)

        # Run Elasticsearch (query body is in search_queries.py)
        response = es.search(
            index=config.SEARCH_INDEX,
            body=build_product_search(request.query, request.page, request.page_size),
        )

        hits = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            source["_score"] = hit.get("_score")
            hits.append(source)

        total = response["hits"]["total"]["value"]
        took_ms = response["took"]

        # Outcome metrics for analytics (zero-results rate, latency, etc.)
        span.set_attribute("search.result_count", total)
        span.set_attribute("search.took_ms", took_ms)
        span.set_attribute(
            "search.query_response_hit_ids",
            [h["id"] for h in hits[:20]],
        )

        return {
            "hits": hits,
            "total": total,
            "took_ms": took_ms,
            "query_id": query_id,
        }


# =============================================================================
# BLOG 3: Click tracking — uncomment to enable
#
# Also uncomment matching blocks in frontend/app.js
# Traffic: python generate_traffic.py --blog 3 --sessions 50
# Queries: queries/blog3_click_quality.esql
# =============================================================================

import threading
import time

_clicked_queries: dict[str, float] = {}
_clicked_queries_lock = threading.Lock()


def _is_first_click(query_id: str) -> bool:
    """True once per query_id — enables CTR without double-counting clicks."""
    now = time.time()
    with _clicked_queries_lock:
        cutoff = now - 1800
        for k in [k for k, v in _clicked_queries.items() if v < cutoff]:
            del _clicked_queries[k]
        if query_id in _clicked_queries:
            return False
        _clicked_queries[query_id] = now
        return True


class ClickEvent(BaseModel):
    object_id: str = Field(..., description="Product ID clicked")
    position: int = Field(..., ge=1, description="1-based position in results")
    query_id: Optional[str] = None
    client_id: Optional[str] = None
    user_query: Optional[str] = None
    object_id_type: str = "product"


@app.post("/api/events")
async def track_click(event: ClickEvent):
    with tracer.start_as_current_span("search.result.click") as span:
        span.set_attribute("search.action", "click")
        span.set_attribute("search.result_click_id", event.object_id)
        span.set_attribute("search.result_click_position", event.position)
        span.set_attribute("search.result_click_type", event.object_id_type)
        if event.query_id:
            span.set_attribute("search.query_id", event.query_id)
        if event.client_id:
            span.set_attribute("enduser.pseudo.id", event.client_id)
        if event.user_query:
            span.set_attribute("search.query", event.user_query.lower().strip())
        if event.query_id and _is_first_click(event.query_id):
            span.set_attribute("search.first_click", True)  # native boolean
        return {"status": "ok", "query_id": event.query_id}


# =============================================================================
# BLOG 4: Conversion tracking — uncomment to enable (requires Blog 3)
#
# Also uncomment frontend/app.js and index.html cart button
# Traffic: python generate_traffic.py --blog 4 --sessions 100
# Queries: queries/blog4_conversions.esql
# =============================================================================

class CartEvent(BaseModel):
    object_id: str
    position: int = Field(..., ge=1)
    query_id: Optional[str] = None
    client_id: Optional[str] = None
    user_query: Optional[str] = None
    quantity: int = 1
    price: Optional[float] = None


@app.post("/api/cart/add")
async def add_to_cart(event: CartEvent):
    with tracer.start_as_current_span("cart.add") as span:
        span.set_attribute("search.action", "add_to_cart")
        span.set_attribute("search.result_click_id", event.object_id)
        span.set_attribute("search.result_click_position", event.position)
        span.set_attribute("cart.quantity", event.quantity)
        if event.price is not None:
            span.set_attribute("cart.price", event.price)
        if event.query_id:
            span.set_attribute("search.query_id", event.query_id)
        if event.client_id:
            span.set_attribute("enduser.pseudo.id", event.client_id)
        if event.user_query:
            span.set_attribute("search.query", event.user_query.lower().strip())
        return {"status": "ok"}


class CheckoutItem(BaseModel):
    object_id: str
    quantity: int = 1
    price: float


class CheckoutEvent(BaseModel):
    order_id: str
    total_amount: float
    items: List[CheckoutItem] = []
    client_id: Optional[str] = None
    query_id: Optional[str] = None
    user_query: Optional[str] = None


@app.post("/api/checkout")
async def checkout(event: CheckoutEvent):
    with tracer.start_as_current_span("checkout.complete") as span:
        span.set_attribute("search.action", "purchase")
        span.set_attribute("checkout.order_id", event.order_id)
        span.set_attribute("checkout.total_amount", event.total_amount)
        span.set_attribute("checkout.item_count", len(event.items))
        if event.client_id:
            span.set_attribute("enduser.pseudo.id", event.client_id)
        if event.query_id:
            span.set_attribute("search.query_id", event.query_id)
        if event.user_query:
            span.set_attribute("search.query", event.user_query.lower().strip())
        return {"status": "ok", "order_id": event.order_id}


# =============================================================================
# Run locally
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    print(f"\n  Search Analytics Demo: http://localhost:{config.PORT}\n")
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
