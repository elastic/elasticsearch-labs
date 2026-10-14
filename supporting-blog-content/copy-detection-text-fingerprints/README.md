# Fingerprint copy check demo

Detect copied text with stock Elasticsearch, no plugin. Protected documents are indexed as overlapping 8-word
phrases ("fingerprints"). Paste any text, and the demo returns the protected documents it copies from and
highlights the copied words on both sides.

It works on Elastic Cloud Serverless 9.x and self-managed Elasticsearch 9.x. Everything needed is in this folder.

## What it shows
- Index analyzer `fingerprint_8`: standard tokenizer, lowercase, asciifolding, `shingle` (8 words, no unigrams).
  The `body` field uses it with `index_options: offsets` (see `mappings/index.json`).
- One query per check (`check.py`): a plain `match` on the raw text finds candidates, the match rule filters them,
  and the unified highlighter returns the copied passage of the protected document.
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
Values in `.env` override the shell environment.

## Commands
```bash
python load_data.py                          # 2,000 patents + 8 phishing templates (about a minute)
python load_data.py --patents 500            # smaller
python load_data.py --from-folder ~/docs     # your own .txt / .md files instead (cut at 9,000 words each)
streamlit run app.py                         # the UI on http://localhost:8501
python cli.py --file email.txt --rule min_shared --n 3
python cli.py "paste text here" --rule verified_run --n 16 --exclude-common 5
pytest tests -q                              # real cluster tests, throwaway index
python cleanup.py                            # delete the index
```

## Matching rules
The input is fingerprinted with the same analyzer. Duplicates in the input are removed first, so a repeated phrase
counts once.
- **any**: at least 1 shared fingerprint. Most sensitive, and shared stock phrases will trigger it.
- **min_shared N**: at least N distinct shared fingerprints (a bool `should` of `term` queries with
  `minimum_should_match: N`). N shared fingerprints in a row mean a copied run of N + 7 words.
- **verified_run N** (default 16 words): the match must also contain a copied passage of at least N words in a row,
  measured on the highlighted passage. This is the evidence tier.
- **Ignore common phrases**: phrases found in many protected documents are dropped from the query. Find them in the
  "Common phrases" tab, or `--exclude-common`.

The query JSON is shown in the UI (expander) and returned by `check()`.

## Limits
- Each distinct fingerprint in the input is one query clause. Keep inputs to a few thousand words, and
  `_analyze` rejects more than 10,000 tokens.
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
