from elasticsearch import Elasticsearch, helpers
from openai import Embedding
import json
import os

# Global variables
# Modify these if you want to use a different file, index or model
FILE = 'sample_data/medicare.json'
INDEX = 'openai-integration'
MODEL = 'text-embedding-ada-002'
ELASTIC_CLOUD_ID = os.getenv('ELASTIC_CLOUD_ID')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
OPENAI_API_TOKEN = os.getenv('OPENAI_API_TOKEN')


def maybe_create_index(es_client: Elasticsearch):
    # Check if index exists, if not create it
    if es_client.indices.exists(index=INDEX):
        return

    print(f'Creating index {INDEX}...')

    try:
        es_client.indices.create(
            index=INDEX,
            settings={
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                }
            },
            mappings={
                "properties": {
                    "url": {
                        "type": "keyword"
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "english"
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "english"
                    },
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 1536,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        )
    except Exception as e:
        print(f'Error while creating index: {e}')
        exit(1)


def bulk_index_docs(docs, es_client):
    # Create actions for bulk indexing
    # See https://elasticsearch-py.readthedocs.io/en/master/helpers.html#bulk-helpers for details
    actions = []
    for doc in docs:
        action = {
            "_op_type": "index",
            "_index": INDEX,
            "_id": doc["url"],
            "_source": doc,
        }
        actions.append(action)

    print(f"Indexing {len(docs)} documents to index {INDEX}...")

    try:
        helpers.bulk(es_client, actions)
    except Exception as e:
        print(f'Error while indexing documents: {e}')
        exit(1)


def generate_embeddings_with_openai(docs):
    # Generate OpenAI embeddings from the content of the documents
    # See https://platform.openai.com/docs/api-reference/embeddings for details
    input = [doc['content'] for doc in docs]

    print(f'Calling OpenAI API for {len(input)} embeddings with model {MODEL}')

    try:
        result = Embedding.create(engine=MODEL, input=input)
        return [data['embedding'] for data in result['data']]
    except Exception as e:
        print(f'Error while using OpenAI API: {e}')
        exit(1)


def process_file():
    print(f'Reading from file {FILE}')

    # Read the JSON documents from the file
    with open(FILE, 'r') as in_file:
        docs = json.load(in_file)

        print(f'Processing {len(docs)} documents...')

        # Split the list of documents into batches of 10
        batch_size = 10
        docs_batches = [docs[i:i + batch_size] for i in range(0, len(docs), batch_size)]
        for docs_batch in docs_batches:
            print(f'Processing batch of {len(docs_batch)} documents...')
            
            # Generate embeddings and add them to the documents
            embeddings = generate_embeddings_with_openai(docs_batch)
            for i, doc in enumerate(docs_batch):
                doc['embedding'] = embeddings[i]

            # Index batch of documents
            bulk_index_docs(docs_batch, es_client)

            # Uncomment these lines if you're hitting the OpenAI rate limit due to the number of requests
            # print('Sleeping for 2 seconds to avoid reaching OpenAI rate limit...')
            # time.sleep(2)

    print('Processing complete')


if __name__ == "__main__":
    print(f'Connecting to Elastic Cloud: {ELASTIC_CLOUD_ID}')

    # Connect to Elastic Cloud
    es_client = Elasticsearch(cloud_id=ELASTIC_CLOUD_ID, basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD))

    maybe_create_index(es_client)
    process_file()
