"""Core logic: is this text copied from a protected document? Uses stock Elasticsearch only.

check(es, index, text, rule, n) runs ONE search:
  must    match on `body` with the raw text (the field analyzer fingerprints the query too)
  filter  bool/should of term queries on the unique query fingerprints, minimum_should_match = N
  highlight  unified highlighter on `body` with a match on the raw text -> copied passages of the matched doc
Rules: "any" (>= 1 shared fingerprint), "min_shared" (>= N), "verified_run" (longest copied run >= N words).
"""

from dataclasses import dataclass, field

from spans import PRE, POST, merge, parse_marked, word_count

ANALYZER = "fingerprint_8"
RULES = ("any", "min_shared", "verified_run")


@dataclass
class Match:
    id: str
    title: str
    collection: str
    score: float
    matched: int  # distinct shared fingerprints
    longest_run: int  # words in the longest copied passage
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
    return es.indices.analyze(index=index, analyzer=ANALYZER, text=text)["tokens"]


def build_query(text: str, fps: list[str], n: int) -> dict:
    should = [{"term": {"body": f}} for f in fps]
    return {
        "bool": {
            "must": [{"match": {"body": {"query": text}}}],
            "filter": [{"bool": {"should": should, "minimum_should_match": n}}],
        }
    }


def _spans_on_input(
    tokens: list[dict], doc_fps: set[str], text: str
) -> list[tuple[int, int]]:
    return merge(
        [(t["start_offset"], t["end_offset"]) for t in tokens if t["token"] in doc_fps],
        text,
    )


def check(
    es,
    index: str,
    text: str,
    rule: str = "any",
    n: int = 3,
    exclude: set[str] | None = None,
    size: int = 20,
) -> Result:
    """Find protected documents that share fingerprints with `text` under the chosen rule."""
    tokens = analyze(es, index, text)
    fps = sorted({t["token"] for t in tokens} - (exclude or set()))
    need = n if rule == "min_shared" else 1
    if not fps:
        return Result(rule, n, 0, text, [], {})
    query = build_query(text, fps, need)
    hl = {
        "type": "unified",
        "pre_tags": [PRE],
        "post_tags": [POST],
        "number_of_fragments": 0,
        # match (not terms): a large terms highlight_query fails on long texts ("bytes can be at most 32766").
        "highlight_query": {"match": {"body": text}},
    }
    resp = es.search(
        index=index,
        size=size,
        query=query,
        highlight={"fields": {"body": hl}},
        _source=["title", "collection"],
    )
    matches = []
    for h in resp["hits"]["hits"]:
        marked = h.get("highlight", {}).get("body", [""])[0]
        doc_text, dspans = parse_marked(marked)
        dspans = merge(dspans, doc_text)
        run = max((word_count(doc_text, s) for s in dspans), default=0)
        if rule == "verified_run" and run < n:
            continue
        doc_fps = {t["token"] for t in analyze(es, index, doc_text)} & set(fps)
        matches.append(
            Match(
                h["_id"],
                h["_source"].get("title", ""),
                h["_source"].get("collection", ""),
                h["_score"],
                len(doc_fps),
                run,
                doc_text,
                dspans,
                _spans_on_input(tokens, doc_fps, text),
            )
        )
    return Result(
        rule,
        n,
        len(fps),
        text,
        matches,
        {"query": query, "highlight": {"fields": {"body": hl}}},
    )
