"""Small helpers for highlight tags and character spans."""

PRE, POST = "", ""  # private-use chars, cannot clash with real text


def parse_marked(marked: str) -> tuple[str, list[tuple[int, int]]]:
    """Strip highlight tags; return (plain text, merged char spans)."""
    plain, spans, start, depth = [], [], 0, 0
    for ch in marked:
        if ch == PRE:
            if depth == 0:
                start = len(plain)
            depth += 1
        elif ch == POST:
            depth -= 1
            if depth == 0:
                spans.append((start, len(plain)))
        else:
            plain.append(ch)
    return "".join(plain), spans


def merge(spans: list[tuple[int, int]], text: str) -> list[tuple[int, int]]:
    """Merge spans that overlap or are separated only by whitespace."""
    out: list[tuple[int, int]] = []
    for s, e in sorted(spans):
        if out and (s <= out[-1][1] or not text[out[-1][1] : s].strip()):
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
