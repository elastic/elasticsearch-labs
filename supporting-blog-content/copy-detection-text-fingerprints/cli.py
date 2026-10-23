"""Check text against the protected index.

  python cli.py "text to check"
  python cli.py --file email.txt --rule min_shared --n 3
  cat email.txt | python cli.py --rule any
  python cli.py --file email.txt --rule verified_run --n 16 --exclude-common 5
Copied words are marked [[like this]].
"""

import argparse
import sys

from boilerplate import deny_list
from check import DEFAULT_N, RULES, CheckError, check
from es import get_client, index_name
from spans import mark


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("text", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--rule", choices=RULES, default="verified_run")
    ap.add_argument(
        "--n",
        type=int,
        default=None,
        help="N for min_shared (fingerprints, default 3) or verified_run (words, default 16)",
    )
    ap.add_argument("--index", help="index name (default: INDEX_NAME in .env)")
    ap.add_argument(
        "--exclude-common",
        type=int,
        default=0,
        metavar="DOCS",
        help="skip phrases found in at least this many protected docs",
    )
    a = ap.parse_args()
    if a.file:
        with open(a.file, encoding="utf-8") as fh:
            text = fh.read()
    elif a.text:
        text = a.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        ap.error("give the text, --file, or pipe text on stdin")
    es, idx = get_client(), a.index or index_name()
    if not es.indices.exists(index=idx):
        sys.exit(f"Index '{idx}' not found. Load data first: python load_data.py")
    excl = deny_list(es, idx, a.exclude_common) if a.exclude_common else set()
    try:
        res = check(es, idx, text, a.rule, a.n, excl)
    except CheckError as e:
        sys.exit(str(e))
    shown_n = "" if a.rule == "any" else f" n={res.n}"
    print(
        f"rule={a.rule}{shown_n}  input fingerprints={res.fingerprints}  matches={len(res.matches)}"
    )
    if not res.fingerprints:
        print("no fingerprints: the text needs at least 8 words in a row")
        return
    for m in res.matches:
        print(
            f"\n== {m.title} [{m.collection}]  score={m.score:.1f}  shared={m.matched}  longest run={m.longest_run} words"
        )
        print("-- input:  ", mark(text, m.input_spans).replace("\n", " ")[:1500])
        for s, e in m.doc_spans[:5]:
            print("-- matched doc passage:", m.doc_text[s:e].replace("\n", " ")[:600])
    if not res.matches:
        print("no match")


if __name__ == "__main__":
    main()
