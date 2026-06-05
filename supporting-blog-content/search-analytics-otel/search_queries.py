"""Elasticsearch query bodies for the product search API.

Kept separate from app.py so the tutorial code stays focused on OTel spans.
"""


def build_product_search(query: str, page: int, page_size: int) -> dict:
    """BM25 text search with rank_feature boosts for popularity, margin, etc."""
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
