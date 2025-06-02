import os
import json
from dotenv import load_dotenv

from elastic_client import es
from elasticsearch import helpers

from sentence_transformers import SentenceTransformer


load_dotenv(override=True)

INDEX_NAME = f"{os.environ.get('INDEX_NAME')}-pipeline"

# Delete the indices if they already exist
es.indices.delete(index=f"{INDEX_NAME}", ignore_unavailable=True)
es.indices.delete(index=f"failed-{INDEX_NAME}", ignore_unavailable=True)


# This function creates an ingest pipeline that uses the sentence-transformers library
# to embed the book descriptions.
# More information here:
# https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-text-emb-vector-search-example.html
def create_ingest_pipeline():
    resp = es.ingest.put_pipeline(
        id="text-embedding",
        description="converts book description text to a vector",
        processors=[
            {
                "inference": {
                    "model_id": "sentence-transformers__msmarco-minilm-l-12-v3",
                    "input_output": [
                        {
                            "input_field": "book_description",
                            "output_field": "description_embedding",
                        }
                    ],
                }
            }
        ],
        on_failure=[
            {
                "set": {
                    "description": "Index document to 'failed-<index>'",
                    "field": "_index",
                    "value": "failed-{{{_index}}}",
                }
            },
            {
                "set": {
                    "description": "Set error message",
                    "field": "ingest.failure",
                    "value": "{{_ingest.on_failure_message}}",
                }
            },
        ],
    )
    print(f"Created ingest pipeline: {resp}")


# This function creates the Elasticsearch index with the appropriate mappings.
def create_books_index():
    mappings = {
        "mappings": {
            "properties": {
                "book_title": {"type": "text"},
                "author_name": {"type": "text"},
                "rating_score": {"type": "float"},
                "rating_votes": {"type": "integer"},
                "review_number": {"type": "integer"},
                "book_description": {"type": "text"},
                "genres": {"type": "keyword"},
                "year_published": {"type": "integer"},
                "url": {"type": "text"},
            }
        }
    }

    es.indices.create(index=INDEX_NAME, body=mappings)
    print(f"Index '{INDEX_NAME}' created.")


def create_one_book(book):

    try:
        resp = es.index(
            index=INDEX_NAME,
            id=book.get("id", None),
            body=book,
            pipeline="text-embedding",
        )

        print(
            f"Successfully indexed book: {book.get('book_title', None)} - Result: {resp.get('result', None)}"
        )

    except Exception as e:
        print(f"Error occurred while indexing book: {e}")


def bulk_ingest_books(file_path="../data/books.json"):
    with open(file_path, "r") as file:
        books = json.load(file)

    actions = [
        {"_index": INDEX_NAME, "_id": book.get("id", None), "_source": book}
        for book in books
    ]

    try:
        print(f"Indexing {len(actions)} documents...")
        helpers.bulk(es, actions, pipeline="text-embedding", chunk_size=1000)
        print(f"Successfully ingested books into the '{INDEX_NAME}' index.")

    except helpers.BulkIndexError as e:
        print(f"Error occurred while ingesting books: {e}")


create_books_index()
create_ingest_pipeline()
bulk_ingest_books()


with open("../data/one_book.json", "r") as file:
    book = json.load(file)
    create_one_book(book)
