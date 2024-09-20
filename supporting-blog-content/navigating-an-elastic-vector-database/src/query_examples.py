import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from elastic_client import es

load_dotenv(override=True)

# This file uses the 'books-pipeline' index, which is created in the 'upload_books_local_embed.py' file.
# If you wish to use the 'books-local' index, change the below line to:
#  'INDEX_NAME = f"{os.environ.get('INDEX_NAME')}-local"'
INDEX_NAME = f'{os.environ.get("INDEX_NAME")}-pipeline'
MODEL_ID = os.environ.get("MODEL_ID")


def vector_search(query_string):
    search_result = es.search(
        index=INDEX_NAME,
        knn={
            "field": "description_embedding",
            "k": 10,
            "num_candidates": 50,
            "query_vector_builder": {
                "text_embedding": {"model_id": MODEL_ID, "model_text": query_string}
            },
        },
    )
    return search_result


def search(query_string):
    search_result = es.search(
        index=INDEX_NAME, body={"query": {"match": {"book_description": query_string}}}
    )

    return search_result


def hybrid_search(query_string):
    search_result = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query_string,
                                "fields": [
                                    "book_title",
                                    "author_name",
                                    "book_description",
                                ],
                            }
                        },
                    ]
                }
            },
            "knn": {
                "field": "description_embedding",
                "k": 10,
                "query_vector_builder": {
                    "text_embedding": {"model_id": MODEL_ID, "model_text": query_string}
                },
            },
            "rank": {"rrf": {}},
            "size": 10,
        },
    )
    return search_result


def print_results(search_result):
    print(f"Total hits: {search_result['hits']['total']['value']}")
    for hit in search_result["hits"]["hits"]:
        print(f"Book: {hit['_source']['book_title']}")
        print(f"Author: {hit['_source']['author_name']}")
        print(f"Description: {hit['_source']['book_description']}")
        print(f"Score: {hit['_score']}")
        print("")


query_string = "Dinosaurs are still alive"
vector_results = vector_search(query_string)
print_results(vector_results)
bm25_results = search(query_string)
print_results(bm25_results)
hybrid_results = hybrid_search(query_string)
print_results(hybrid_results)
