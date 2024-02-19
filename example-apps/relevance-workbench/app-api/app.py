from flask import Flask, request, jsonify
import os
from elasticsearch import Elasticsearch

CLOUD_ID = os.environ["CLOUD_ID"]
ES_USER = os.environ["ELASTICSEARCH_USERNAME"]
ES_PASSWORD = os.environ["ELASTICSEARCH_PASSWORD"]

datasets = {
    "movies": {
        "id": "movies",
        "label": "Movies",
        "index": "search-movies",
        "search_fields": ["title", "overview", "keywords"],
        "elser_search_fields": [
            "ml.inference.overview_expanded.predicted_value",
            "ml.inference.title_expanded.predicted_value^0.5",
        ],
        "result_fields": ["title", "overview"],
        "mapping_fields": {"text": "overview", "title": "title"},
    }
}

app = Flask(__name__)


@app.route("/api/search/<index>")
def route_api_search(index):
    """
    Execute the search
    """
    [query, rrf, type, k, datasetId] = [
        request.args.get("q"),
        request.args.get("rrf", default=False, type=lambda v: v.lower() == "true"),
        request.args.get("type", default="bm25"),
        request.args.get("k", default=0),
        request.args.get("dataset", default="movies"),
    ]
    if type == "elser":
        search_result = run_semantic_search(
            query, index, **{"rrf": rrf, "k": k, "dataset": datasetId}
        )
    elif type == "bm25":
        search_result = run_full_text_search(query, index, **{"dataset": datasetId})
    transformed_search_result = transform_search_response(
        search_result, datasets[datasetId]["mapping_fields"]
    )
    return jsonify(response=transformed_search_result)


@app.route("/api/datasets", methods=["GET"])
def route_api_datasets():
    """
    Return the available datasets
    """
    return datasets


@app.errorhandler(404)
def resource_not_found(e):
    """
    Return a JSON response of the error and the URL that was requested
    """
    return jsonify(error=str(e)), 404


def get_text_expansion_request_body(query, size=10, **options):
    """
    Generates an ES text expansion search request.
    """
    fields = datasets[options["dataset"]]["elser_search_fields"]
    result_fields = datasets[options["dataset"]]["result_fields"]
    text_expansions = []
    boost = 1

    for field in fields:

        split_field_descriptor = field.split("^")
        if len(split_field_descriptor) == 2:
            boost = split_field_descriptor[1]
            field = split_field_descriptor[0]
        te = {"text_expansion": {}}
        te["text_expansion"][field] = {
            "model_text": query,
            "model_id": ".elser_model_1",
            "boost": boost,
        }
        text_expansions.append(te)
    return {
        "_source": False,
        "fields": result_fields,
        "size": size,
        "query": {"bool": {"should": text_expansions}},
    }


def get_text_expansion_request_body(query, size=10, **options):
    """
    Generates an ES text expansion search request.
    """
    fields = datasets[options["dataset"]]["elser_search_fields"]
    result_fields = datasets[options["dataset"]]["result_fields"]
    text_expansions = []
    boost = 1

    for field in fields:

        split_field_descriptor = field.split("^")
        if len(split_field_descriptor) == 2:
            boost = split_field_descriptor[1]
            field = split_field_descriptor[0]
        te = {"text_expansion": {}}
        te["text_expansion"][field] = {
            "model_text": query,
            "model_id": ".elser_model_1",
            "boost": boost,
        }
        text_expansions.append(te)
    return {
        "_source": False,
        "fields": result_fields,
        "size": size,
        "query": {"bool": {"should": text_expansions}},
    }


def get_text_search_request_body(query, size=10, **options):
    """
    Generates an ES full text search request.
    """
    fields = datasets[options["dataset"]]["result_fields"]
    search_fields = datasets[options["dataset"]]["search_fields"]
    return {
        "_source": False,
        "fields": fields,
        "size": size,
        "query": {"multi_match": {"query": query, "fields": search_fields}},
    }


def get_hybrid_search_rrf_request_body(query, size=10, **options):
    """
    Generates an ES hybrid search with RRF
    """
    fields = datasets[options["dataset"]]["elser_search_fields"]
    result_fields = datasets[options["dataset"]]["result_fields"]
    search_fields = datasets[options["dataset"]]["search_fields"]
    text_expansions = []
    boost = 1

    for field in fields:

        split_field_descriptor = field.split("^")
        if len(split_field_descriptor) == 2:
            boost = split_field_descriptor[1]
            field = split_field_descriptor[0]
        te = {"text_expansion": {}}
        te["text_expansion"][field] = {
            "model_text": query,
            "model_id": ".elser_model_1",
            "boost": boost,
        }
        text_expansions.append(te)
    return {
        "_source": False,
        "fields": result_fields,
        "size": size,
        "rank": {"rrf": {"window_size": 10, "rank_constant": 2}},
        "sub_searches": [
            {"query": {"bool": {"should": text_expansions}}},
            {"query": {"multi_match": {"query": query, "fields": search_fields}}},
        ],
    }


def execute_search_request(index, body):
    """
    Executes an ES search request and returns the JSON response.
    """
    es = Elasticsearch(cloud_id=CLOUD_ID, basic_auth=(ES_USER, ES_PASSWORD))
    response = es.search(
        index=index,
        query=body["query"],
        fields=body["fields"],
        size=body["size"],
        source=body["_source"],
    )

    return response


def execute_search_request_using_raw_dsl(index, body):
    """
    Executes an ES search request using the request library and returns the JSON response.
    """

    es = Elasticsearch(cloud_id=CLOUD_ID, basic_auth=(ES_USER, ES_PASSWORD))
    response = es.perform_request(
        "POST",
        f"/{index}/_search",
        headers={"content-type": "application/json", "accept": "application/json"},
        body=body,
    )

    return response


def run_full_text_search(query, index, **options):
    """
    Runs a full text search on the given index using the passed query.
    """
    if query is None or query.strip() == "":
        raise Exception("Query cannot be empty")
    body = get_text_search_request_body(query, **options)
    response = execute_search_request(index, body)

    return response["hits"]["hits"]


def run_semantic_search(query, index, **options):
    """
    Runs a semantic search of the provided query on the target index, and reranks the KNN and BM25 results.
    """
    if options.get("rrf") == True:
        body = get_hybrid_search_rrf_request_body(query, **options)
        # Execute the request using the raw DSL to avoid the ES Python client since sub_searches query are not supported yet
        response_json = execute_search_request_using_raw_dsl(index, body)
    else:
        body = get_text_expansion_request_body(query, **options)
        print(body)
        response_json = execute_search_request(index, body)

    return response_json["hits"]["hits"]


def find_id_index(id: int, hits: list):
    """
    Finds the index of an object in `hits` which has _id == `id`.
    """

    for i, v in enumerate(hits):
        if v["_id"] == id:
            return i + 1
    return 0


def transform_search_response(searchResults, mappingFields):
    for hit in searchResults:
        fields = hit["fields"]
        hit["fields"] = {
            "text": fields[mappingFields["text"]],
            "title": fields[mappingFields["title"]],
        }
    return searchResults
