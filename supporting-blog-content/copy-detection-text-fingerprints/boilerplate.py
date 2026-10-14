"""Find boilerplate: fingerprints (8-word phrases) shared by many protected documents.

`body` is an analyzed text field, so it cannot be used in a terms aggregation or ES|QL. Instead:
  1. read the term vectors of a random sample of documents (_mtermvectors) and count phrases seen twice or more;
  2. get exact document counts for the best candidates with ONE `filters` aggregation (term vector doc_freq is
     per shard, so it understates the index-wide count).
Phrases are readable text because they are shingles. A phrase more common than the sample can see may be missed.
"""

from collections import Counter


def common_phrases(
    es, index: str, min_docs: int = 5, limit: int = 50, sample: int = 500
) -> list[tuple[str, int]]:
    """Return [(phrase, doc_count)] for phrases in >= min_docs documents, most common first."""
    hits = es.search(
        index=index,
        size=sample,
        _source=False,
        query={
            "function_score": {
                "query": {"match_all": {}},
                "random_score": {"seed": 7, "field": "_seq_no"},
            }
        },
    )
    ids = [h["_id"] for h in hits["hits"]["hits"]]
    seen: Counter = Counter()
    for i in range(0, len(ids), 50):
        resp = es.mtermvectors(
            index=index,
            ids=ids[i : i + 50],
            fields=["body"],
            positions=False,
            offsets=False,
            payloads=False,
            field_statistics=False,
            term_statistics=False,
        )
        for doc in resp["docs"]:
            seen.update(
                doc.get("term_vectors", {}).get("body", {}).get("terms", {}).keys()
            )
    cands = [t for t, c in seen.most_common(max(3 * limit, 100)) if c >= 2]
    if not cands:
        return []
    aggs = {"f": {"filters": {"filters": {t: {"term": {"body": t}} for t in cands}}}}
    buckets = es.search(index=index, size=0, aggs=aggs)["aggregations"]["f"]["buckets"]
    counts = sorted(
        ((t, b["doc_count"]) for t, b in buckets.items() if b["doc_count"] >= min_docs),
        key=lambda x: -x[1],
    )
    return counts[:limit]


def deny_list(
    es, index: str, min_docs: int = 5, limit: int = 2000, sample: int = 500
) -> set[str]:
    """Phrases to exclude from matching: removed from the query fingerprints before the search."""
    return {p for p, _ in common_phrases(es, index, min_docs, limit, sample)}
