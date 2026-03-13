# Search Analytics with OpenTelemetry and Elastic

A minimal reference project for the blog series **"Search Analytics with OTel and Elastic"**. Clone it, set your Elastic Cloud credentials, and have search analytics data flowing in 10 minutes.

## What This Demonstrates

- **Blog 2**: Search API instrumented with OpenTelemetry — every search creates a span with `search.*` attributes, queryable via ES|QL
- **Blog 3**: Click tracking with CTR and MRR metrics
- **Blog 4**: Conversion funnel from search to purchase
- **Blog 6**: SLO definitions, burn rate alerting, and operational dashboards

The project starts with Blog 2 active. Blogs 3 and 4 are present but commented out — uncomment them as you progress through the series.

## Architecture

```
┌──────────────┐        ┌──────────────┐        ┌──────────────────┐
│   Browser    │──POST──│   FastAPI     │──query──│  Elasticsearch   │
│  (frontend)  │  /api  │   (app.py)   │         │  (product data)  │
└──────────────┘        └──────┬───────┘        └──────────────────┘
                               │
                          OTLP/HTTP
                               │
                        ┌──────▼───────┐
                        │  Elastic APM  │
                        │  (traces)     │
                        └──────────────┘
```

## Prerequisites

- **Python 3.10+**
- **Elastic Cloud account** with:
  - A deployment for product data (Elasticsearch)
  - APM enabled (for trace ingestion) — can be the same deployment or separate

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url>
cd search-analytics-otel
cp .env.example .env
```

Edit `.env` with your Elastic Cloud credentials:

| Variable | Where to find it |
|----------|-----------------|
| `ELASTICSEARCH_URL` | Elastic Cloud console → your deployment → Elasticsearch endpoint |
| `ELASTIC_API_KEY` | Kibana → Stack Management → API Keys → Create |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Kibana → Observability → APM → Settings → APM Server URL |
| `OTEL_EXPORTER_OTLP_HEADERS` | Same page → Secret token (format: `Authorization=Bearer <token>`) |

### 2. Setup and load data

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python load_data.py
```

### 3. Start the server

```bash
python app.py
```

Open http://localhost:8000 — search for "laptop", "headphones", "running shoes".

### 4. Generate traffic and explore

```bash
python generate_traffic.py --blog 2 --sessions 20
```

Then in Kibana → Discover, switch to ES|QL mode and run:

```sql
FROM traces-apm-*
| WHERE service.name == "search-analytics-demo" AND span.name == "search"
| KEEP labels.search_user_query, numeric_labels.search_result_count, numeric_labels.search_took_ms
| SORT @timestamp DESC
| LIMIT 10
```

See `queries/blog2_search_analytics.esql` for more queries.

---

## Blog Walkthrough

### Blog 2: Search Instrumentation (Active by Default)

The `POST /api/search` endpoint in `app.py` creates an OTel span named `search` with these attributes:

| Attribute | ES|QL Field | Description |
|-----------|------------|-------------|
| `search.user_query` | `labels.search_user_query` | Query text |
| `search.query_id` | `labels.search_query_id` | Unique ID (trace ID) |
| `search.result_count` | `numeric_labels.search_result_count` | Total matching results |
| `search.took_ms` | `numeric_labels.search_took_ms` | Elasticsearch execution time |
| `search.application` | `labels.search_application` | Service identifier |
| `search.index` | `labels.search_index` | Index searched |

**Try these queries** from `queries/blog2_search_analytics.esql`:
- Top queries by volume
- Zero-results rate
- Latency percentiles (p50/p95/p99)
- Which queries return zero results

### Blog 3: Click Tracking

**Enable it:**

1. In `app.py`: uncomment the **BLOG 3** section (click endpoint + first-click tracking)
2. In `frontend/app.js`: uncomment the **BLOG 3** sections (trackClick function + click handlers)
3. Restart the server: `python app.py`
4. Generate traffic: `python generate_traffic.py --blog 3 --sessions 50`

New attributes on click spans:

| Attribute | ES|QL Field | Description |
|-----------|------------|-------------|
| `search.action` | `labels.search_action` | `"click"` |
| `search.result_click_id` | `labels.search_result_click_id` | Product ID clicked |
| `search.result_click_position` | `numeric_labels.search_result_click_position` | Position in results (1-based) |
| `search.first_click` | `labels.search_first_click` | `"true"` if first click for this query |
| `search.client_id` | `labels.search_client_id` | Browser identifier |

**Key gotcha:** `search.first_click` is a boolean in OTel but stored as a **string** (`"true"`/`"false"`) in Elastic APM. Query it with `labels.search_first_click == "true"`, not as a native boolean.

**Try these queries** from `queries/blog3_click_quality.esql`:
- Overall CTR (click-through rate)
- CTR by query (find low-performing queries)
- MRR (mean reciprocal rank)
- Click position distribution

### Blog 4: Conversion Tracking

**Enable it** (requires Blog 3 to be enabled first):

1. In `app.py`: uncomment the **BLOG 4** section (cart + checkout endpoints)
2. In `frontend/app.js`: uncomment the **BLOG 4** sections (addToCart function + button handlers)
3. In `frontend/index.html`: uncomment the `.cart-btn` CSS styles and the cart button HTML in `app.js`
4. Restart the server: `python app.py`
5. Generate traffic: `python generate_traffic.py --blog 4 --sessions 100`

**Try these queries** from `queries/blog4_conversions.esql`:
- Full conversion funnel (search → click → cart → purchase)
- Revenue by query
- Most clicked products with cart rates

### Blog 6: Search Reliability (Kibana Configuration)

No code changes needed — Blog 6 uses the data already flowing from Blogs 2-4.

**Create three SLOs** in Kibana → Observability → SLOs:

1. **Latency SLO**: APM Latency indicator, service `search-analytics-demo`, threshold 250ms, target 99%
2. **Availability SLO**: APM Availability indicator, target 99.9%
3. **Quality SLO**: Custom KQL on `traces-apm-*`:
   - Good: `span.name: "search" AND numeric_labels.search_result_count > 0`
   - Total: `span.name: "search" AND labels.search_user_query: *`
   - Target: 85%

Each SLO auto-creates a burn rate alert rule. See `queries/blog6_reliability.esql` for dashboard queries.

---

## ES|QL Field Mapping Reference

OTel span attributes are stored by Elastic APM with these transformations:

| Rule | Example |
|------|---------|
| Dots become underscores | `search.user_query` → `search_user_query` |
| Strings go to `labels.*` | `search.user_query` → `labels.search_user_query` |
| Numbers go to `numeric_labels.*` | `search.result_count` → `numeric_labels.search_result_count` |
| Booleans stored as strings | `search.first_click` → `labels.search_first_click` (`"true"`/`"false"`) |

---

## Configuration

### Two-Cluster Setup (Recommended for Production)

Use separate Elastic Cloud deployments:
- **Search cluster**: hosts your product index
- **Observability cluster**: receives APM traces, runs ES|QL analytics

This ensures observability load doesn't affect search performance.

### Single-Cluster Setup (Fine for Testing)

Point both `ELASTICSEARCH_URL` and `OTEL_EXPORTER_OTLP_ENDPOINT` to the same deployment. Everything works the same — the deployment handles both product data and APM traces.

---

## Project Structure

```
├── app.py                    # FastAPI backend (single file, ~300 lines)
├── products.json             # 80 curated ecommerce products
├── index_mapping.json        # Elasticsearch index mapping with rank_features
├── load_data.py              # Index products into Elasticsearch
├── generate_traffic.py       # Simulate realistic user sessions
├── frontend/
│   ├── index.html            # Minimal search UI
│   └── app.js                # Search, click, cart handlers
├── queries/
│   ├── blog2_search_analytics.esql
│   ├── blog3_click_quality.esql
│   ├── blog4_conversions.esql
│   └── blog6_reliability.esql
├── .env.example              # Environment variable template
├── requirements.txt          # Python dependencies
└── setup.sh                  # One-command setup
```
