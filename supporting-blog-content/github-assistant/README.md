# GitHub Assistant

Easily ask questions about your GitHub repository using RAG and Elasticsearch as a Vector database.

### How to use this code

1. Install Required Libraries:

```bash
pip install -r requirements.txt
```

2. Set Up Environment Variables
`GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH`, `ELASTIC_CLOUD_ID`, `ELASTIC_USER`, `ELASTIC_PASSWORD`, `ELASTIC_INDEX`, `OPENAI_API_KEY`

3. Index your data and create the embeddings by running:

```bash
python index.py
```

An Elasticsearch index will be generated, housing the embeddings. You can then connect to your ESS deployment and run search query against the index, you will see a new field named embeddings.

4. Ask questions about your codebase by running:

```bash
python query.py
```