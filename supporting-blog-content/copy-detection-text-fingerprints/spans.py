"""Small helpers for character spans."""


def es_offsets(text: str):
    """Elasticsearch offsets count UTF-16 code units, Python strings count characters (code points). Return a
    function mapping an Elasticsearch offset in `text` to a Python index (identity when there are no emoji etc.).
    """
    if all(ord(c) <= 0xFFFF for c in text):
        return lambda o: o
    table = []
    for i, c in enumerate(text):
        table.append(i)
        if ord(c) > 0xFFFF:  # two UTF-16 code units, one Python character
            table.append(i)
    table.append(len(text))
    return lambda o: table[min(o, len(table) - 1)]


def merge(spans: list[tuple[int, int]], text: str) -> list[tuple[int, int]]:
    """Merge spans that overlap or are separated only by whitespace (for display)."""
    out: list[tuple[int, int]] = []
    for s, e in sorted(spans):
        if out and (s <= out[-1][1] or not text[out[-1][1] : s].strip()):
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def runs(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge only spans that overlap. Consecutive fingerprints overlap by 7 words, so each result is one unbroken
    copied run. Two copied pieces that merely sit next to each other stay separate."""
    out: list[tuple[int, int]] = []
    for s, e in sorted(spans):
        if out and s < out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def word_count(text: str, span: tuple[int, int]) -> int:
    return len(text[span[0] : span[1]].split())


def mark(
    text: str, spans: list[tuple[int, int]], pre: str = "[[", post: str = "]]"
) -> str:
    out, cur = [], 0
    for s, e in spans:
        out += [text[cur:s], pre, text[s:e], post]
        cur = e
    out.append(text[cur:])
    return "".join(out)
