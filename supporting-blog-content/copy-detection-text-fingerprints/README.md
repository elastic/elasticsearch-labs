# Fingerprint copy check demo

Detect copied text with stock Elasticsearch, no plugin. Protected documents are indexed as overlapping 8-word
phrases ("fingerprints"). Paste any text, and the demo returns the protected documents it copies from and
highlights the copied words on both sides.

It works on Elastic Cloud Serverless 9.x and self-managed Elasticsearch 9.x. Everything needed is in this folder.

## What it shows
- Index analyzer `fingerprint_8`: standard tokenizer, lowercase, asciifolding, `shingle` (8 words, no unigrams).
  The `body` field uses it with `index_options: offsets` (see `mappings/index.json`).
- Search analyzer `fingerprint_8_search`: the same chain plus the stop filter `boilerplate_stop`, which drops
  boilerplate phrases from queries. The index keeps every phrase.
- One search per check (`check.py`): a plain `match` query with the whole input text. The search analyzer turns
  the text into fingerprints on the server. The unified highlighter marks the copied words in the matched protected
  document; `_analyze` marks them in the input.
- Boilerplate: find phrases shared by many documents, then apply them as stop words (`boilerplate.py`).
- Two sample collections: patents (leakage of internal documents) and phishing email templates (cyber).

## Prerequisites
- Python 3.10+ and an Elasticsearch 9.x endpoint with an API key that can create indices.
- Internet access on the first load (BigPatent downloads one parquet shard from Hugging Face).

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env        # then edit ES_URL, ES_API_KEY, INDEX_NAME
```
Values in `.env` override the shell environment, so to use another index edit `INDEX_NAME` in `.env` or pass
`--index` to `load_data.py` and `cli.py` (and the name to `cleanup.py`).

## Commands
```bash
python load_data.py                          # 2,000 patents + 8 phishing templates (about a minute)
python load_data.py --patents 500            # smaller
python load_data.py --from-folder ~/docs     # your own .txt / .md files instead (cut at about 9,000 tokens each)
python load_data.py --recreate               # replace an existing index (without it, an existing index is kept)
streamlit run app.py                         # the UI on http://localhost:8501
python cli.py --file email.txt --rule min_shared --n 3
python cli.py "paste text here" --rule verified_run --n 16
cat email.txt | python cli.py --rule any
python cli.py --file email.txt --boilerplate # count boilerplate stop words too (classification)
python stopwords.py --find 5                 # phrases in >= 5 documents
python stopwords.py --apply 5                # make them stop words (reopens the index)
python stopwords.py --show | --clear
pytest tests -q                              # real cluster tests, throwaway index
python cleanup.py                            # delete the index
```

## Matching rules
The input is fingerprinted with the same analyzer. Duplicates in the input are removed first, so a repeated phrase
counts once.
- **any**: at least 1 shared fingerprint. Most sensitive, and shared stock phrases will trigger it.
- **min_shared N** (default 3): at least N distinct shared fingerprints. The query uses `minimum_should_match: N`,
  which counts a phrase repeated in the input each time, so the demo then checks the distinct count. N shared
  fingerprints in a row mean a copied run of N + 7 tokens (the standard tokenizer splits hyphenated words, so this
  can be more than N + 7 words).
- **verified_run N** (default 16 words): the input must also contain a copied passage of at least N words in a row:
  an unbroken chain of overlapping shared fingerprints. Two short copies that sit apart in the input do not add up.
  This is the evidence tier.

The query JSON is shown in the UI (expander) and returned by `check()`.

## Boilerplate as stop words
Disclaimers, signatures and stock phrases cause most false alarms in leak checks, but they are exactly what
identifies a template or document type. So the index keeps them, and only the search analyzer drops them:
1. Find them: the "Common phrases" tab or `python stopwords.py --find 5`. A sample of documents is read with
   `_mtermvectors`, and one `filters` aggregation counts the candidates exactly.
2. Apply them: "Apply as stop words" or `--apply 5`. This runs `PUT <index>/_settings?reopen=true`, which closes the
   index, updates the `boilerplate_stop` list and reopens it in one call (also on Serverless). Searches pause while
   the index reopens; on Serverless they can fail for some seconds.
3. Leak checks stay a plain `match`, and stop-word phrases neither find documents nor count as evidence.
4. Classification: "Count boilerplate too" or `--boilerplate` matches with the index analyzer
   (`"analyzer": "fingerprint_8"`), so boilerplate counts again.

`?reopen=true` can only change a filter that already exists: it acknowledges, but ignores, new analysis components.
That is why the filter is defined (with `"_none_"`) when the index is created. Indices created by older versions of
this demo need `python load_data.py --recreate`. Applying stop words needs the `manage` index privilege.

## Limits
- `_analyze` accepts at most 10,000 tokens, so inputs are limited to roughly 9,000 words; longer inputs get a
  "text is too long" message. Each distinct fingerprint is one query clause, and the clause limit
  (`indices.query.bool.max_clause_count`) depends on heap size, so a small self-managed node may refuse long inputs
  sooner. The demo reports this instead of failing.
- Edits break every 8-word phrase that contains them, so heavy paraphrase is not detected.
- The boilerplate finder samples 500 documents (`sample=`), so very rare shared phrases can be missed.

## Sample data
- Patents: BigPatent, config `a` (Sharma, Li and Wang, "BIGPATENT: A Large-Scale Dataset for Abstractive and
  Coherent Summarization", ACL 2019), licensed CC BY 4.0. Source:
  https://huggingface.co/datasets/NortheasternUniversity/big_patent. Descriptions are cut to 2,000 words.
- Phishing templates (`data/phishing_templates.json`): written for this demo, fictional, no real brands.
- Email corpus (optional, for your own tests): the Enron Email Dataset, William W. Cohen, MLD, Carnegie Mellon
  University, https://www.cs.cmu.edu/~enron/. Not downloaded by this demo.

## Cleanup
`python cleanup.py` deletes the index. Remove `.env` when you are done, as it holds your API key.
