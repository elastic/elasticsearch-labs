"""Mini UI: paste text, see which protected documents it copies from, with copied words highlighted.
Run: streamlit run app.py
"""

import html
import json

import streamlit as st

import examples
from boilerplate import common_phrases, deny_list
from check import check
from es import get_client, index_name

st.set_page_config(page_title="Fingerprint copy check", layout="wide")
st.markdown(
    """<style>
html, body, [class*="css"], .stTextArea textarea { font-size: 19px !important; }
.box { background:#161b26; border:1px solid #3a4258; border-radius:8px; padding:14px; line-height:1.65;
       white-space:pre-wrap; max-height:420px; overflow:auto; color:#f2f4f8; }
mark { background:#ffb454; color:#10131a; padding:1px 2px; border-radius:3px; font-weight:600; }
</style>""",
    unsafe_allow_html=True,
)


@st.cache_resource
def client():
    return get_client()


@st.cache_data(show_spinner=False)
def cached_deny(index: str, min_docs: int) -> set[str]:
    return deny_list(client(), index, min_docs)


def render(text: str, spans: list[tuple[int, int]], limit: int | None = None) -> str:
    """HTML with copied spans in <mark>. For long documents show only the area around the copied passages."""
    if limit and len(text) > limit and spans:
        a, b = max(0, spans[0][0] - 400), min(len(text), spans[-1][1] + 400)
        text, spans = text[a:b], [(s - a, e - a) for s, e in spans if e > a and s < b]
        spans = [(max(s, 0), min(e, len(text))) for s, e in spans]
    out, cur = [], 0
    for s, e in spans:
        out += [html.escape(text[cur:s]), "<mark>", html.escape(text[s:e]), "</mark>"]
        cur = e
    out.append(html.escape(text[cur:]))
    return f'<div class="box">{"".join(out)}</div>'


def short_query(q: dict) -> dict:
    """The sent query with the long term list cut to 5 clauses (the real one has one per fingerprint)."""
    q = json.loads(json.dumps(q))
    f = q["query"]["bool"]["filter"][0]["bool"]
    f["should"] = (
        f["should"][:5] + [f"... {len(f['should']) - 5} more term clauses"]
        if len(f["should"]) > 5
        else f["should"]
    )
    t = q["highlight"]["fields"]["body"]["highlight_query"]["terms"]
    t["body"] = t["body"][:5] + ["..."] if len(t["body"]) > 5 else t["body"]
    return q


idx = index_name()
st.title("Copy check with stock Elasticsearch")
st.caption(
    f"Index: {idx}. Each protected document is stored as overlapping 8-word phrases (fingerprints)."
)

if "text" not in st.session_state:
    st.session_state.text = ""
with st.sidebar:
    st.header("Match rule")
    rules = {
        "Any shared fingerprint": "any",
        "At least N shared fingerprints": "min_shared",
        "Verified run of at least N words": "verified_run",
    }
    rule = rules[st.radio("Rule", list(rules), index=1)]
    n = 3
    if rule == "min_shared":
        n = st.slider("N (fingerprints)", 1, 30, 3)
    elif rule == "verified_run":
        n = st.slider("N (words)", 8, 60, 16)
    excl = st.slider(
        "Ignore phrases found in at least this many documents (0 = off)", 0, 50, 0
    )

tab_check, tab_common = st.tabs(["Check text", "Common phrases (boilerplate)"])

with tab_check:
    cols = st.columns(4)
    ex = examples.build(client(), idx)
    for col, (label, body) in zip(cols, ex.items()):
        if col.button(label, width="stretch"):
            st.session_state.text = body
    text = st.text_area("Text to check", key="text", height=190)
    # Any button click reruns the script with the latest text, so this just gives the rerun a visible trigger.
    st.button(":material/search: Check text", type="primary")
    st.caption(
        "Edit the text, then select Check text (or press Ctrl+Enter / Cmd+Enter in the box)."
    )
    if text.strip():
        res = check(
            client(), idx, text, rule, n, cached_deny(idx, excl) if excl else None
        )
        st.subheader(f"{len(res.matches)} protected document(s) matched")
        st.write(f"Input has {res.fingerprints} distinct fingerprints.")
        for m in res.matches:
            with st.container(border=True):
                st.markdown(f"### {m.title}  \n`{m.collection}`")
                a, b, c = st.columns(3)
                a.metric("Score", f"{m.score:.1f}")
                b.metric("Shared fingerprints", m.matched)
                c.metric("Longest copied run", f"{m.longest_run} words")
                left, right = st.columns(2)
                left.markdown("**Your text**")
                left.markdown(render(text, m.input_spans), unsafe_allow_html=True)
                right.markdown("**Protected document**")
                right.markdown(
                    render(m.doc_text, m.doc_spans, limit=2500), unsafe_allow_html=True
                )
        with st.expander("Query JSON"):
            st.json(short_query(res.query), expanded=True)

with tab_common:
    st.write(
        "Phrases shared by many protected documents. They cause false alarms, so exclude them or require more "
        "than one shared phrase."
    )
    min_docs = st.slider("Minimum documents", 2, 50, 5, key="mind")
    if st.button("Find common phrases"):
        rows = common_phrases(client(), idx, min_docs, 40)
        st.dataframe(
            [{"phrase": p, "documents": d} for p, d in rows], use_container_width=True
        )
