"""Check text against the protected index.

  python cli.py "text to check"
  python cli.py --file email.txt --rule min_shared --n 3
  python cli.py --file email.txt --rule verified_run --n 16 --exclude-common 5
Copied words are marked [[like this]].
"""

import argparse
import sys

from boilerplate import deny_list
from check import RULES, check
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
        default=16,
        help="N for min_shared (fingerprints) or verified_run (words)",
    )
    ap.add_argument(
        "--exclude-common",
        type=int,
        default=0,
        metavar="DOCS",
        help="skip phrases found in at least this many protected docs",
    )
    a = ap.parse_args()
    text = open(a.file).read() if a.file else (a.text or sys.stdin.read())
    es, idx = get_client(), index_name()
    excl = deny_list(es, idx, a.exclude_common) if a.exclude_common else set()
    res = check(es, idx, text, a.rule, a.n, excl)
    print(
        f"rule={a.rule} n={a.n}  input fingerprints={res.fingerprints}  matches={len(res.matches)}"
    )
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
