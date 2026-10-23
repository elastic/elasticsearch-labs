# Fingerprint copy check demo

Detect copied text with stock Elasticsearch, no plugin. Protected documents are indexed as overlapping 8-word
phrases ("fingerprints"). Paste any text, and the demo returns the protected documents it copies from and
highlights the copied words on both sides.

It works on Elastic Cloud Serverless 9.x and self-managed Elasticsearch 9.x. Everything needed is in this folder.

## What it shows
- Index analyzer `fingerprint_8`: standard tokenizer, lowercase, asciifolding, `shingle` (8 words, no unigrams).
  The `body` field uses it with `index_options: offsets` (see `mappings/index.json`).
- One search per check (`check.py`): the input is fingerprinted with `_analyze`, and a bool `should` of `term`
  queries (one per distinct fingerprint, `minimum_should_match` from the rule) finds the protected documents.
  One `_mtermvectors` call then gives the offsets of the shared fingerprints in each match, so the copied words are
  highlighted on both sides.
- Two sample collections: patents (leakage of internal documents) and phishing email templates (cyber).
- A boilerplate finder that lists phrases shared by many documents.

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
python cli.py "paste text here" --rule verified_run --n 16 --exclude-common 5
cat email.txt | python cli.py --rule any
pytest tests -q                              # real cluster tests, throwaway index
python cleanup.py                            # delete the index
```

## Matching rules
The input is fingerprinted with the same analyzer. Duplicates in the input are removed first, so a repeated phrase
counts once.
- **any**: at least 1 shared fingerprint. Most sensitive, and shared stock phrases will trigger it.
- **min_shared N** (default 3): at least N distinct shared fingerprints (`minimum_should_match: N`). N shared
  fingerprints in a row mean a copied run of N + 7 tokens (the standard tokenizer splits hyphenated words, so this
  can be more than N + 7 words).
- **verified_run N** (default 16 words): the input must also contain a copied passage of at least N words in a row:
  an unbroken chain of overlapping shared fingerprints. Two short copies that sit apart in the input do not add up.
  This is the evidence tier.
- **Ignore common phrases**: phrases found in many protected documents are dropped from the input fingerprints, so
  they neither find documents nor count as evidence. Find them in the "Common phrases" tab, or `--exclude-common`.

The query JSON is shown in the UI (expander) and returned by `check()`.

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
