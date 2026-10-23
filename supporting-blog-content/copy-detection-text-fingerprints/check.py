"""Core logic: is this text copied from a protected document? Uses stock Elasticsearch only.

check(es, index, text, rule, n):
  1. ONE search: a plain `match` with the whole text. The field's analyzer turns the text into fingerprints on the
     server, so the client never builds them. minimum_should_match = N for min_shared. The score grows with the
     number of shared fingerprints. With an exclude list (boilerplate), a filter also requires at least one
     non-excluded fingerprint.
  2. _analyze the text with the same analyzer -> its fingerprints with offsets, to show where the copied words are
     in the input. ONE _mtermvectors call gives the same for each matched protected document.
Evidence is computed from the shared, non-excluded fingerprints on both sides, counted once each (the match query
counts a phrase repeated in the input every time, so min_shared is checked exactly on the distinct ones). The
copied run is measured on the input: consecutive shared fingerprints overlap, so an unbroken chain of them is one
copied passage.
Rules: "any" (>= 1 shared fingerprint), "min_shared" (>= N), "verified_run" (copied run >= N words).
"""

from dataclasses import dataclass, field

from elasticsearch import BadRequestError

from spans import es_offsets, merge, runs, word_count

ANALYZER = "fingerprint_8"
RULES = ("any", "min_shared", "verified_run")
DEFAULT_N = {"any": 1, "min_shared": 3, "verified_run": 16}


class CheckError(Exception):
    """A problem with the input that the user can fix (too long, too many fingerprints)."""


@dataclass
class Match:
    id: str
    title: str
    collection: str
    score: float
    matched: int  # distinct shared fingerprints (after exclusions)
    longest_run: int  # words in the longest unbroken copied passage of the input
    doc_text: str
    doc_spans: list = field(default_factory=list)  # char spans in the matched doc
    input_spans: list = field(default_factory=list)  # char spans in the input text


@dataclass
class Result:
    rule: str
    n: int
    fingerprints: int  # distinct fingerprints in the input (after exclusions)
    text: str
    matches: list
    query: dict


def analyze(es, index: str, text: str) -> list[dict]:
    """Fingerprints of `text` with char offsets, using the index analyzer."""
    try:
        return es.indices.analyze(index=index, analyzer=ANALYZER, text=text)["tokens"]
    except BadRequestError as e:
        if "max_token_count" in str(e) or "allowed maximum" in str(e):
            raise CheckError(
                "The text is too long: Elasticsearch analyzes at most 10,000 tokens per request. "
                "Check a shorter part (a few thousand words)."
            ) from e
        raise


def build_query(text: str, n: int = 1, keep: list[str] | None = None) -> dict:
    """`match` on the whole text. keep = the non-excluded fingerprints, only when an exclude list is in use."""
    match = {"query": text}
    if n > 1:
        match["minimum_should_match"] = n
    query = {"match": {"body": match}}
    if keep is None:
        return query
    should = [{"term": {"body": f}} for f in keep]
    return {
        "bool": {
            "must": [query],
            "filter": [{"bool": {"should": should, "minimum_should_match": 1}}],
        }
    }


def _doc_offsets(es, index: str, ids: list[str]) -> dict[str, dict]:
    """{doc id: {fingerprint: [(start, end), ...]}} from term vectors (computed on the fly from _source)."""
    resp = es.mtermvectors(
        index=index,
        ids=ids,
        fields=["body"],
        offsets=True,
        positions=False,
        payloads=False,
        field_statistics=False,
        term_statistics=False,
    )
    out = {}
    for d in resp["docs"]:
        terms = d.get("term_vectors", {}).get("body", {}).get("terms", {})
        out[d["_id"]] = {
            t: [(x["start_offset"], x["end_offset"]) for x in v.get("tokens", [])]
            for t, v in terms.items()
        }
    return out


def check(
    es,
    index: str,
    text: str,
    rule: str = "any",
    n: int | None = None,
    exclude: set[str] | None = None,
    size: int = 20,
) -> Result:
    """Find protected documents that share fingerprints with `text` under the chosen rule."""
    n = DEFAULT_N[rule] if n is None else n
    tokens = analyze(es, index, text)
    fps = sorted({t["token"] for t in tokens} - (exclude or set()))
    need = n if rule == "min_shared" else 1
    query = build_query(text, need, fps if exclude else None)
    if not fps:
        return Result(rule, n, 0, text, [], {"query": query})
    try:
        resp = es.search(
            index=index,
            size=size,
            query=query,
            _source=["title", "collection", "body"],
        )
    except BadRequestError as e:
        if "too_many" in str(e) or "maxClauseCount" in str(e):
            raise CheckError(
                f"The text has {len(fps)} distinct fingerprints, more query clauses than this cluster allows "
                "(indices.query.bool.max_clause_count). Check a shorter part."
            ) from e
        raise
    hits = resp["hits"]["hits"]
    doc_offsets = _doc_offsets(es, index, [h["_id"] for h in hits]) if hits else {}
    to_py = es_offsets(text)
    in_offsets: dict[str, list] = {}
    for t in tokens:
        in_offsets.setdefault(t["token"], []).append(
            (to_py(t["start_offset"]), to_py(t["end_offset"]))
        )
    matches = []
    for h in hits:
        doc_text = h["_source"].get("body", "")
        terms = doc_offsets.get(h["_id"], {})
        shared = set(fps) & terms.keys()
        in_spans = [s for f in shared for s in in_offsets[f]]
        run = max((word_count(text, s) for s in runs(in_spans)), default=0)
        if len(shared) < need or (rule == "verified_run" and run < n):
            continue
        doc_py = es_offsets(doc_text)
        dspans = [(doc_py(s), doc_py(e)) for f in shared for s, e in terms[f]]
        matches.append(
            Match(
                h["_id"],
                h["_source"].get("title", ""),
                h["_source"].get("collection", ""),
                h["_score"],
                len(shared),
                run,
                doc_text,
                merge(dspans, doc_text),
                merge(in_spans, text),
            )
        )
    return Result(rule, n, len(fps), text, matches, {"query": query})
